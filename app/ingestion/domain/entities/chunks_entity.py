import re
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from chat.domain.exceptions.domain_exceptions import InvalidEntityException

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
        return cls(
            id=uuid4(),
            source_id=source_id,
            study_subject=study_subject,
            content=Content(content),
            embedding=Embedding(embedding),
            created_at=datetime.now(timezone.utc)
        )

    @classmethod
    def from_db_dict(cls, db_dict: dict) -> "Chunk":
        emb_data = db_dict["embedding"]
        
        if isinstance(emb_data, str):
            clean_emb = [float(x) for x in re.findall(r'-?\d+\.?\d*', emb_data)]
        else:
            clean_emb = emb_data

        return cls(
            id=UUID(db_dict["id"]),
            source_id=UUID(db_dict["source_id"]),
            study_subject=UUID(db_dict["study_subject"]),
            content=Content(db_dict["content"]),
            embedding=Embedding(clean_emb),
            created_at=datetime.fromisoformat(db_dict["created_at"])
        )