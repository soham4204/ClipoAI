import uuid
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import structlog

from app.database import get_db, async_session_factory
from app.models import Video, Job, Transcript, Clip
from app.api.auth import get_current_user

logger = structlog.get_logger()
router = APIRouter()

async def run_analysis_job(job_id: uuid.UUID, video_id: uuid.UUID, transcript_text: str, words_json: list):
    """
    Background task to analyze the transcript using Gemini and save Clips.
    """
    logger.info("Starting background analysis job", job_id=str(job_id), video_id=str(video_id))
    
    # We must create a new session for the background task
    async with async_session_factory() as session:
        # Update job to running
        job = await session.get(Job, job_id)
        if not job:
            return
            
        job.status = "running"
        await session.commit()
        
        try:
            from app.services.ai_analyzer import AIAnalyzerService
            
            analyzer = AIAnalyzerService()
            clip_recommendations = analyzer.analyze_transcript(transcript_text, words_json)
            
            # Save clips to database
            for rec in clip_recommendations:
                # The recommendation is a dict (or Pydantic model dict dump)
                # Since we used JSON output, it comes as a dict.
                new_clip = Clip(
                    video_id=video_id,
                    title=rec.get("title", "Untitled Clip"),
                    start_time_sec=rec.get("start_time_sec", 0.0),
                    end_time_sec=rec.get("end_time_sec", 0.0),
                    viral_score=rec.get("viral_score", 0),
                    status="generated"
                )
                session.add(new_clip)
                
            job.status = "completed"
            await session.commit()
            logger.info("Analysis job completed successfully", job_id=str(job_id), clips_found=len(clip_recommendations))
            
        except Exception as e:
            logger.error("Analysis job failed", job_id=str(job_id), error=str(e))
            job.status = "failed"
            job.error_message = str(e)
            await session.commit()


@router.post("/{video_id}", response_model=Dict[str, Any])
async def trigger_analysis(
    video_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger AI analysis for a video that has been transcribed.
    """
    # 1. Check if video exists and belongs to user
    result = await db.execute(select(Video).where(Video.id == video_id, Video.user_id == current_user.id))
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
    # 2. Get the latest transcript
    result = await db.execute(
        select(Transcript).where(Transcript.video_id == video_id).order_by(Transcript.created_at.desc())
    )
    transcript = result.scalars().first()
    
    if not transcript:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No transcript found for this video. Transcribe it first.")
        
    # 3. Check for existing active analysis jobs
    result = await db.execute(
        select(Job).where(
            Job.video_id == video_id, 
            Job.type == "analysis",
            Job.status.in_(["queued", "running"])
        )
    )
    existing_job = result.scalars().first()
    if existing_job:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Analysis is already in progress for this video")
        
    # 4. Create new job
    job = Job(
        video_id=video.id,
        type="analysis",
        status="queued"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # 5. Queue background task
    background_tasks.add_task(
        run_analysis_job, 
        job.id, 
        video.id, 
        transcript.text,
        transcript.words_json
    )
    
    return {
        "message": "Analysis job queued successfully",
        "job_id": str(job.id),
        "video_id": str(video.id)
    }
