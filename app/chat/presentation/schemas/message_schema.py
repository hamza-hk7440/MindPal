from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from chat.domain.value_objects.message_objects import Role

class SendMessageRequest(BaseModel):
    conversation_id: UUID = Field(..., description="The ID of the conversation to which the message belongs.")
    content: str = Field(..., description="The content of the message.")
    sender_role: Role = Field(..., description="The role of the sender (e.g., 'user', 'assistant').")

    class Config:
        from_attributes = True
        use_enum_values = True
class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    content: str
    sender: Role
    created_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True