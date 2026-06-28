"""
Pydantic Schemas for Videos.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class YouTubeIngestRequest(BaseModel):
    """Payload for ingesting a YouTube video."""
    url: HttpUrl


class VideoBase(BaseModel):
    """Base video attributes."""
    title: str
    source_type: str
    source_url: Optional[str] = None
    status: str = "pending"


class VideoCreate(VideoBase):
    """Attributes needed to create a video."""
    user_id: UUID
    storage_path: Optional[str] = None
    metadata_json: Dict[str, Any] = {}


class VideoResponse(VideoBase):
    """Attributes returned when reading a video."""
    id: UUID
    user_id: UUID
    storage_path: Optional[str] = None
    metadata_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
