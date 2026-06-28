"""
YouTube integration service using yt-dlp.
"""
import os
import tempfile
import uuid
from typing import Dict, Tuple

import structlog
import yt_dlp

from app.services.storage import storage_service

logger = structlog.get_logger()


class YouTubeService:
    """Handles downloading and metadata extraction from YouTube."""

    def extract_metadata(self, url: str) -> Dict:
        """Extract metadata without downloading the video."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "uploader": info.get("uploader", ""),
                    "view_count": info.get("view_count", 0),
                    "thumbnail": info.get("thumbnail", ""),
                    "source_url": url
                }
        except Exception as e:
            logger.error("Failed to extract YouTube metadata", url=url, error=str(e))
            raise ValueError(f"Invalid or inaccessible YouTube URL: {str(e)}")

    def download_and_store(self, url: str) -> Tuple[str, Dict]:
        """
        Download the best video stream and upload to MinIO.
        Returns (storage_path, metadata).
        """
        # First get metadata
        metadata = self.extract_metadata(url)
        object_name = f"youtube/{uuid.uuid4()}.mp4"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_filepath = os.path.join(tmp_dir, "video.mp4")
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': tmp_filepath,
                'quiet': True,
                'no_warnings': True,
            }
            
            try:
                logger.info("Downloading YouTube video", url=url)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Upload to MinIO
                file_size = os.path.getsize(tmp_filepath)
                logger.info("Uploading YouTube video to MinIO", size=file_size)
                
                with open(tmp_filepath, "rb") as f:
                    storage_path = storage_service.upload_file(
                        object_name=object_name,
                        data=f,
                        length=file_size,
                        content_type="video/mp4"
                    )
                return storage_path, metadata

            except Exception as e:
                logger.error("Failed to download and store YouTube video", url=url, error=str(e))
                raise


youtube_service = YouTubeService()
