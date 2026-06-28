"""
Pydantic Schemas for Users and Authentication.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Payload decoded from JWT."""
    sub: Optional[str] = None


class UserBase(BaseModel):
    """Base user attributes."""
    email: EmailStr
    is_active: bool = True
    role: str = "user"


class UserCreate(UserBase):
    """Attributes needed to create a new user."""
    password: str


class UserRead(UserBase):
    """Attributes returned when reading a user."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
