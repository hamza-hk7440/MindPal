from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from chat.domain.exceptions.domain_exceptions import (InvalidEntityException,
                                                             BusinessRuleViolationException)

@dataclass(frozen=True)
class Conversation:
    subject_id: UUID
    title: str
    id: UUID | None = None
    created_at: datetime | None = None

    def __post_init__(self):
        if self.id is None:
            object.__setattr__(self, "id", uuid4())
        if not self.title or self.title.strip() == "":
            raise InvalidEntityException("Conversation title cannot be empty.")
        now = datetime.now(self.created_at.tzinfo) if self.created_at and self.created_at.tzinfo else datetime.now()
        if self.created_at and self.created_at > now:
            raise BusinessRuleViolationException("Conversation creation time cannot be in the future.")
