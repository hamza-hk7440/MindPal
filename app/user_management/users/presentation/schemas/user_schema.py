from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    id: UUID
    display_name: str
    email: str
    role: str
    bio: str
    favorite_subjects: list[str] = Field(default_factory=list)
    updated_at: datetime | None = None


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    favorite_subjects: list[str] | None = None


class UserSummaryResponse(BaseModel):
    id: UUID
    display_name: str
    email: str
    role: str