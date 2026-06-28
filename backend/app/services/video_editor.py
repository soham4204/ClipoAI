import os
import tempfile
import uuid
from typing import Optional
import ffmpeg
import structlog
from minio.error import S3Error

from app.services.storage import storage_service

logger = structlog.get_logger()

class VideoEditorService:
    """Handles video editing operations using FFmpeg."""

    def __init__(self):
        pass

    def generate_clip(self, video_storage_path: str, clip_id: uuid.UUID, start_time_sec: float, end_time_sec: float) -> str:
        """
        Downloads original video, trims, crops to 9:16, and uploads the clip.
        Returns the new storage path of the clip.
        """
        logger.info("Starting video editing for clip", clip_id=str(clip_id), start=start_time_sec, end=end_time_sec)
        
        if not video_storage_path:
            raise ValueError("Invalid storage path")
            
        parts = video_storage_path.split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid storage path format: {video_storage_path}")
            
        bucket_name, object_name = parts[0], parts[1]
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_filepath = os.path.join(tmp_dir, "input.mp4")
            output_filepath = os.path.join(tmp_dir, f"{clip_id}.mp4")
            
            # 1. Download original video
            logger.info("Downloading original video", object_name=object_name)
            try:
                storage_service.client.fget_object(
                    bucket_name=bucket_name,
                    object_name=object_name,
                    file_path=input_filepath
                )
            except S3Error as e:
                logger.error("Failed to download video from MinIO", error=str(e))
                raise
                
            # 2. Process with FFmpeg (Trim + Center Crop to 9:16)
            logger.info("Running FFmpeg processing")
            try:
                # We use ss and to for accurate trimming
                stream = ffmpeg.input(input_filepath, ss=start_time_sec, to=end_time_sec)
                
                # Apply center crop: crop=w=ih*9/16:h=ih
                # (ih is input height. A 9:16 aspect ratio means width is height * 9 / 16)
                video = stream.video.filter('crop', 'ih*9/16', 'ih')
                audio = stream.audio
                
                # Output requires re-encoding video since we filtered it. Audio can be copied.
                out = ffmpeg.output(
                    video, 
                    audio, 
                    output_filepath, 
                    vcodec='libx264', 
                    acodec='copy',
                    preset='fast',
                    crf=23
                )
                
                # Run ffmpeg, capture stderr for debugging if it fails
                out.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                
            except ffmpeg.Error as e:
                logger.error("FFmpeg processing failed", error=e.stderr.decode('utf8'))
                raise RuntimeError(f"FFmpeg error: {e.stderr.decode('utf8')}")
                
            # 3. Upload processed clip
            clip_object_name = f"clips/{clip_id}.mp4"
            logger.info("Uploading processed clip to storage", object_name=clip_object_name)
            
            try:
                storage_service.client.fput_object(
                    bucket_name=bucket_name,
                    object_name=clip_object_name,
                    file_path=output_filepath,
                    content_type="video/mp4"
                )
            except S3Error as e:
                logger.error("Failed to upload clip to MinIO", error=str(e))
                raise
                
            return f"{bucket_name}/{clip_object_name}"

video_editor_service = VideoEditorService()
