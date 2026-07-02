from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import UUID, uuid4
from ingestion.domain.exceptions.domain_exceptions import (InvalidEntityException)
from ingestion.domain.value_objects.type import Type
@dataclass(frozen=True)
class Title:
    value: str
    def __post_init__(self):
        if not self.value or self.value.strip() == "":
            raise InvalidEntityException("Resource title cannot be empty.")
@dataclass(frozen=True)
class Url:
    value: str
    def __post_init__(self):
        if not self.value or self.value.strip() == "":
            raise InvalidEntityException("Resource URL cannot be empty.")
@dataclass(frozen=True)
class Resource:
    id: UUID
    subject_id: UUID
    type: Type
    title: Title
    url: Url
    created_at: datetime

    @classmethod
    def create(cls, subject_id: UUID, type: Type, title: str, url
: str) -> "Resource":
        """Factory method to ensure valid state from the start."""
        if not isinstance(type, Type):
            raise InvalidEntityException("Type must be a valid Type enum.")
        return cls(
            id=uuid4(),
            subject_id=subject_id,
            type=type,
            title=Title(title),
            url=Url(url),
            created_at=datetime.now(timezone.utc)
        )