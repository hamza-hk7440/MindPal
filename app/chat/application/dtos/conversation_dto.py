from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field,BeforeValidator, ConfigDict

class ConversationDTO(BaseModel):
    id: Annotated[UUID | None, Field(description="The unique identifier of the conversation.")] = None
    subject_id: Annotated[UUID, Field(description="The ID of the subject associated with the conversation.")]
    title: Annotated[str, Field(min_length=1, max_length=255)]
    created_at: Annotated[datetime | None, Field(description="The timestamp when the conversation was created.")] = None
    model_config=ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "12345678-1234-5678-1234-567812345678",
                "subject_id": "12345678-1234-5678-1234-567812345678",
                "title": "Project Discussion",
                "created_at": "2023-10-01T12:00:00Z"
            }
        }
    )