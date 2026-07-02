from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class CreateConversationRequest(BaseModel):
    subject_id: UUID = Field(..., description="The ID of the subject associated with the conversation.")
class ConversationResponse(BaseModel):
    id: UUID
    subject_id: UUID
    title: str
    created_at: datetime | None = None
    class Config:
        from_attributes = True
