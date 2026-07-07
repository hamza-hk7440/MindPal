from dataclasses import dataclass
from uuid import UUID
from chat.domain.events.base import DomainEvent

@dataclass(frozen=True)
class SplitChunkEvent(DomainEvent):
    resource_id: UUID
    chunk_id: UUID
    subject_id: UUID
@dataclass(frozen=True)
class VectorizeChunkEvent(DomainEvent):
    resource_id: UUID
    chunk_id: UUID
    subject_id: UUID
@dataclass(frozen=True)
class GetRelevantChunksEvent(DomainEvent):
    subject_id: UUID
    query: str
@dataclass(frozen=True)
class SaveChunkEvent(DomainEvent):
    chunk_id: UUID
    subject_id: UUID
    content: str
@dataclass(frozen=True)
class GetChunkEvent(DomainEvent):
    chunk_id: UUID
    subject_id: UUID