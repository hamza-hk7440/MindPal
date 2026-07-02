from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from chat.domain.value_objects.message_objects import Role
from chat.domain.exceptions.domain_exceptions import (InvalidEntityException,
                                                             BusinessRuleViolationException)

@dataclass(frozen=True)
class ChatMessage:
    conversation_id: UUID
    content: str
    sender: Role
    id: UUID | None = None
    created_at: datetime | None = None

    def __post_init__(self):
        self._initialize_defaults()
        self._validate_content()
        self._validate_sender()
        self._validate_timestamp()

    def _initialize_defaults(self):
        if self.id is None:
            object.__setattr__(self, "id", uuid4())
        if self.created_at is None:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def _validate_content(self):
        if not self.content or self.content.strip() == "":
            raise InvalidEntityException("Message content cannot be empty.")

    def _validate_sender(self):
        if not isinstance(self.sender, Role):
            raise InvalidEntityException("Sender must be a valid Role.")

    def _validate_timestamp(self):
        now = datetime.now(self.created_at.tzinfo) if self.created_at and self.created_at.tzinfo else datetime.now()
        if self.created_at and self.created_at > now:
            raise BusinessRuleViolationException("Message creation time cannot be in the future.")