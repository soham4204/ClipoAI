"""
Videos API routes.
"""
import uuid
from typing import Any, List

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user, get_db
from app.models import User, Video
from app.schemas.video import VideoResponse, YouTubeIngestRequest
from app.services.storage import storage_service
from app.services.youtube import youtube_service

logger = structlog.get_logger()
router = APIRouter()


@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Upload a local video file directly to MinIO.
    """
    if not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video"
        )

    # 1. Upload to MinIO
    object_name = f"uploads/{uuid.uuid4()}_{file.filename}"
    try:
        # File object can be passed directly to MinIO, but we need its size.
        # Spooling might be needed if file doesn't have size, but FastAPI UploadFile provides size optionally.
        # Fallback to reading it to memory if necessary, or just rely on -1 with chunking.
        storage_path = storage_service.upload_file(
            object_name=object_name,
            data=file.file,
            length=file.size or -1,
            content_type=file.content_type
        )
    except Exception as e:
        logger.error("Video upload failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload video to storage"
        )
        
    # 2. Save metadata to Database
    video = Video(
        user_id=current_user.id,
        title=file.filename,
        source_type="local",
        storage_path=storage_path,
        status="processing",
        metadata_json={"content_type": file.content_type, "size": file.size}
    )
    
    db.add(video)
    await db.commit()
    await db.refresh(video)
    
    return video


@router.post("/youtube", response_model=VideoResponse)
async def ingest_youtube(
    request: YouTubeIngestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Ingest a video from a YouTube URL.
    """
    url_str = str(request.url)
    
    # Run the blocking yt-dlp download and MinIO upload in a threadpool
    try:
        storage_path, metadata = await run_in_threadpool(
            youtube_service.download_and_store, url_str
        )
    except Exception as e:
        logger.error("YouTube ingestion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to ingest YouTube video: {str(e)}"
        )
        
    # Save to Database
    video = Video(
        user_id=current_user.id,
        title=metadata.get("title", "YouTube Video"),
        source_type="youtube",
        source_url=url_str,
        storage_path=storage_path,
        status="processing",
        metadata_json=metadata
    )
    
    db.add(video)
    await db.commit()
    await db.refresh(video)
    
    return video


@router.get("/", response_model=List[VideoResponse])
async def list_videos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    List all videos for the current user.
    """
    result = await db.execute(
        select(Video)
        .where(Video.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    videos = result.scalars().all()
    return videos
