from dataclasses import dataclass
from uuid import UUID
from chat.domain.events.base import DomainEvent

@dataclass(frozen=True)
class ConversationCreatedEvent(DomainEvent):
    conversation_id: UUID
    subject_id: UUID
    title: str
