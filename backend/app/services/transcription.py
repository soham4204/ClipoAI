"""
Transcription service utilizing faster-whisper.
"""
import os
import tempfile
import uuid
from typing import Any, Dict

import structlog
from faster_whisper import WhisperModel
from minio.error import S3Error

from app.services.storage import storage_service

logger = structlog.get_logger()


class TranscriptionService:
    """Handles audio transcription using faster-whisper."""

    def __init__(self) -> None:
        # Load the model lazily or initialize here
        # "tiny" or "base" is recommended for CPU environments
        self.model_size = "base"
        self._model = None

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            logger.info("Loading Whisper model", size=self.model_size)
            # Run on CPU with int8 quantization for speed and memory efficiency
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        return self._model

    def transcribe_video(self, storage_path: str) -> Dict[str, Any]:
        """
        Download a video from MinIO, transcribe it, and return the transcript data.
        """
        # Parse bucket and object_name from storage_path
        if not storage_path:
            raise ValueError("Invalid storage path")
            
        parts = storage_path.split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid storage path format: {storage_path}")
            
        bucket_name, object_name = parts[0], parts[1]
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            local_filepath = os.path.join(tmp_dir, f"{uuid.uuid4()}.mp4")
            
            # Download from MinIO
            logger.info("Downloading video for transcription", object_name=object_name)
            try:
                storage_service.client.fget_object(
                    bucket_name=bucket_name,
                    object_name=object_name,
                    file_path=local_filepath
                )
            except S3Error as e:
                logger.error("Failed to download video from MinIO", error=str(e))
                raise
                
            # Transcribe
            logger.info("Starting transcription")
            segments, info = self.model.transcribe(
                local_filepath,
                word_timestamps=True,
                vad_filter=True,
            )
            
            text = ""
            words_data = []
            
            for segment in segments:
                text += segment.text + " "
                for word in segment.words:
                    words_data.append({
                        "word": word.word,
                        "start": word.start,
                        "end": word.end,
                        "probability": word.probability
                    })
                    
            logger.info("Transcription completed", language=info.language, duration=info.duration)
            
            return {
                "text": text.strip(),
                "words_json": words_data,
                "language": info.language
            }


transcription_service = TranscriptionService()
