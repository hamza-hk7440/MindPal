"""Date Trasnfer Object for sending a message."""
from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from chat.domain.value_objects.message_objects import Role
class SendMessageDTO(BaseModel):
    id: Annotated[UUID | None, Field(description="The unique identifier of the message.")] = None
    conversation_id: Annotated[UUID, Field(description="The ID of the conversation to which the message belongs.")]
    content: Annotated[str, Field(min_length=1, max_length=10000)]
    sender: Role
    created_at: Annotated[datetime | None, Field(description="The timestamp when the message was created.")] = None
    model_config=ConfigDict(
        extra="forbid",
        json_schema_extra={

            "example": {
                "id": "12345678-1234-5678-1234-567812345678",
                "conversation_id": "12345678-1234-5678-1234-567812345678",
                "content": "Hello, how are you?",
                "sender": "user",
                "created_at": "2026-07-01T08:45:26.210381"
            }
        }
    )

