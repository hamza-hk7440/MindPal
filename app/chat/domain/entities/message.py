from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import UUID, uuid4

from chat.domain.value_objects.message_objects import Role
from chat.domain.exceptions.domain_exceptions import (InvalidEntityException,
                                                             BusinessRuleViolationException)

@dataclass(frozen=True)
class Content:
    value: str
    def __post_init__(self):
        if not self.value or self.value.strip() == "":
            raise InvalidEntityException("Message content cannot be empty.")

@dataclass(frozen=True)
class ChatMessage:
    conversation_id: UUID
    content: Content
    sender: Role
    id: UUID
    created_at: datetime

    @classmethod
    def create(cls, conversation_id: UUID, content: str, sender: Role) -> "ChatMessage":
        """Factory method to ensure valid state from the start."""
        if not isinstance(sender, Role):
            raise InvalidEntityException("Sender must be a valid Role.")
            
        return cls(
            conversation_id=conversation_id,
            content=Content(content),
            sender=sender,
            id=uuid4(),
            created_at=datetime.now(timezone.utc)
        )