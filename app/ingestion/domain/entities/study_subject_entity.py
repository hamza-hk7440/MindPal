from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import UUID, uuid4
from ingestion.domain.exceptions.domain_exceptions import (InvalidEntityException)

@dataclass(frozen=True)
class Name:
    value: str
    def __post_init__(self):
        if not self.value or self.value.strip() == "":
            raise InvalidEntityException("Study subject name cannot be empty.")
@dataclass(frozen=True)
class StudySubject:
    id: UUID
    user_id: UUID
    name: Name
    created_at: datetime

    @classmethod
    def create(cls, user_id: UUID, name: str) -> "StudySubject":
        """Factory method to ensure valid state from the start."""
        return cls(
            id=uuid4(),
            user_id=user_id,
            name=Name(name),
            created_at=datetime.now(timezone.utc)
        )
