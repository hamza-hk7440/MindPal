from dataclasses import dataclass
from uuid import UUID
from .base import DomainEvent
from chat.domain.value_objects.message_objects import Role

@dataclass(frozen=True)
class SendMessageEvent(DomainEvent):
    message_id: UUID
    conversation_id: UUID
    content: str
    sender: Role

@dataclass(frozen=True)
class GetAllMessagesEvent(DomainEvent):
    conversation_id: UUID