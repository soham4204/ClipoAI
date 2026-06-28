import uuid
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import structlog

from app.database import get_db, async_session_factory
from app.models import Clip, Job, Video
from app.api.auth import get_current_user

logger = structlog.get_logger()
router = APIRouter()

async def run_generation_job(job_id: uuid.UUID, clip_id: uuid.UUID, video_storage_path: str, start_time_sec: float, end_time_sec: float):
    """
    Background task to physically cut and crop the video using FFmpeg.
    """
    logger.info("Starting background generation job", job_id=str(job_id), clip_id=str(clip_id))
    
    async with async_session_factory() as session:
        job = await session.get(Job, job_id)
        if not job:
            return
            
        job.status = "running"
        await session.commit()
        
        try:
            from app.services.video_editor import video_editor_service
            
            # Generate the clip
            new_storage_path = video_editor_service.generate_clip(
                video_storage_path=video_storage_path,
                clip_id=clip_id,
                start_time_sec=start_time_sec,
                end_time_sec=end_time_sec
            )
            
            # Update the clip record
            clip = await session.get(Clip, clip_id)
            if clip:
                clip.storage_path = new_storage_path
                clip.status = "generated"
                
            job.status = "completed"
            await session.commit()
            logger.info("Generation job completed successfully", job_id=str(job_id))
            
        except Exception as e:
            logger.error("Generation job failed", job_id=str(job_id), error=str(e))
            job.status = "failed"
            job.error_message = str(e)
            
            clip = await session.get(Clip, clip_id)
            if clip:
                clip.status = "failed"
            await session.commit()


@router.post("/{clip_id}/generate", response_model=Dict[str, Any])
async def trigger_clip_generation(
    clip_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger video editing for a specific clip recommendation.
    """
    # 1. Fetch clip and verify ownership
    result = await db.execute(
        select(Clip, Video)
        .join(Video, Clip.video_id == Video.id)
        .where(Clip.id == clip_id, Video.user_id == current_user.id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip not found")
        
    clip, video = row[0], row[1]
    
    if clip.status == "generated" and clip.storage_path:
        return {"message": "Clip already generated", "storage_path": clip.storage_path}
        
    if not video.storage_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Original video storage path not found")
        
    # 2. Check for existing active generation jobs for this clip
    # We don't have clip_id directly on Job model natively, but we can check if there's a running job for this video
    # Since Job model only links to video_id, we just create a job and let it run.
    job = Job(
        video_id=video.id,
        type="generation",
        status="queued"
    )
    db.add(job)
    
    # Also update clip status to processing
    clip.status = "processing"
    
    await db.commit()
    await db.refresh(job)
    
    # 3. Queue background task
    background_tasks.add_task(
        run_generation_job, 
        job.id, 
        clip.id, 
        video.storage_path,
        clip.start_time_sec,
        clip.end_time_sec
    )
    
    return {
        "message": "Clip generation job queued successfully",
        "job_id": str(job.id),
        "clip_id": str(clip.id)
    }
