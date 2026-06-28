"""
Transcription API routes.
"""
import uuid
from typing import Any, Dict

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user, get_db
from app.models import Job, Transcript, User, Video
from app.services.transcription import transcription_service

logger = structlog.get_logger()
router = APIRouter()


async def run_transcription_job(job_id: uuid.UUID, video_id: uuid.UUID, storage_path: str, db: AsyncSession) -> None:
    """Background task to run transcription and update DB state."""
    logger.info("Starting background transcription job", job_id=str(job_id), video_id=str(video_id))
    try:
        # 1. Update job to running
        job = await db.get(Job, job_id)
        if job:
            job.status = "running"
            await db.commit()
            
        # 2. Run transcription service (this is blocking, we run it in threadpool or let it block background task thread)
        # BackgroundTasks run in the same event loop if async, or threadpool if def. 
        # Since this is async def, we should yield or use run_in_threadpool. 
        # For simplicity, we'll run it in threadpool.
        from fastapi.concurrency import run_in_threadpool
        result = await run_in_threadpool(transcription_service.transcribe_video, storage_path)
        
        # 3. Save transcript to DB
        transcript = Transcript(
            video_id=video_id,
            text=result["text"],
            words_json=result["words_json"],
            language=result["language"]
        )
        db.add(transcript)
        
        # 4. Update Job and Video status
        if job:
            job.status = "completed"
        video = await db.get(Video, video_id)
        if video:
            video.status = "completed"
            
        await db.commit()
        logger.info("Background transcription job completed successfully", job_id=str(job_id))
        
    except Exception as e:
        logger.error("Background transcription job failed", job_id=str(job_id), error=str(e))
        job = await db.get(Job, job_id)
        if job:
            job.status = "failed"
            job.error_message = str(e)
        video = await db.get(Video, video_id)
        if video:
            video.status = "failed"
        await db.commit()


@router.post("/{video_id}", response_model=Dict[str, Any])
async def trigger_transcription(
    video_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Trigger a background transcription job for a given video.
    """
    # Verify video exists and belongs to user
    video = await db.get(Video, video_id)
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found")
        
    if not video.storage_path:
        raise HTTPException(status_code=400, detail="Video has no storage path yet")
        
    # Create Job record
    job = Job(
        video_id=video.id,
        type="transcription",
        status="queued"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # We must create a new session for the background task to avoid concurrency issues with the current request session
    from app.database import async_session_factory
    
    async def task_wrapper():
        async with async_session_factory() as session:
            await run_transcription_job(job.id, video.id, video.storage_path, session)
            
    # Add to background tasks
    background_tasks.add_task(task_wrapper)
    
    return {
        "message": "Transcription job queued successfully",
        "job_id": job.id,
        "video_id": video.id
    }
