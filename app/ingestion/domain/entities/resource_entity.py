from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import UUID, uuid4
from app.chat.domain.exceptions.domain_exceptions import (InvalidEntityException)
from ingestion.domain.value_objects.type import Doc_type
@dataclass(frozen=True)
class Title:
    value: str
    def __post_init__(self):
        if not self.value or self.value.strip() == "":
            raise InvalidEntityException("Resource title cannot be empty.")
@dataclass(frozen=True)
class Doc_url:
    value: str
    def __post_init__(self):
        if not self.value or self.value.strip() == "":
            raise InvalidEntityException("Resource URL cannot be empty.")
@dataclass(frozen=True)
class Resource:
    id: UUID
    subject_id: UUID
    doc_type: Doc_type
    title: Title
    doc_url: Doc_url
    created_at: datetime

    @classmethod
    def create(cls, subject_id: UUID, doc_type: Doc_type, title: str, doc_url: str) -> "Resource":
        """Factory method to ensure valid state from the start."""
        if not isinstance(doc_type, Doc_type):
            raise InvalidEntityException("Document type must be a valid Doc_type enum.")
        return cls(
            id=uuid4(),
            subject_id=subject_id,
            doc_type=doc_type,
            title=Title(title),
            doc_url=Doc_url(doc_url),
            created_at=datetime.now(timezone.utc)
        )