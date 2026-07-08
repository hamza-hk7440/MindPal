from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import UUID, uuid4
from chat.domain.exceptions.domain_exceptions import (InvalidEntityException)

@dataclass(frozen=True)
class Content:
    value: str
    def __post_init__(self):
        if not self.value or self.value.strip() == "":
            raise InvalidEntityException("Chunk content cannot be empty.")
@dataclass(frozen=True)
class Embedding:
    _values: list[float]
    def __post_init__(self):
        object.__setattr__(self, '_values', self._values)

    def to_list(self) -> list[float]:
        return self._values
@dataclass(frozen=True)
class Chunk:
    id: UUID
    source_id: UUID
    study_subject: UUID
    content: Content
    embedding: Embedding
    created_at: datetime

    @classmethod
    def create(cls, source_id: UUID, study_subject: UUID, content: str, embedding: list[float]) -> "Chunk":
        """Factory method to ensure valid state from the start."""
        return cls(
            id=uuid4(),
            source_id=source_id,
            study_subject=study_subject,
            content=Content(content),
            embedding=Embedding(embedding),
            created_at=datetime.now(timezone.utc)
        )