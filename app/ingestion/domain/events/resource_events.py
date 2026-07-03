from dataclasses import dataclass
from uuid import UUID
from app.chat.domain.events.base import DomainEvent
from ingestion.domain.value_objects.type import Doc_type

@dataclass(frozen=True)
class CreateResourceEvent(DomainEvent):
    resource_id: UUID
    subject_id: UUID
    doc_type: Doc_type
    title: str
    doc_url: str
    content: str
@dataclass(frozen=True)
class GetAllResourcesEvent(DomainEvent):
    subject_id: UUID
@dataclass(frozen=True)
class DeleteResourceEvent(DomainEvent):
    resource_id: UUID
@dataclass(frozen=True)
class GetResourceEvent(DomainEvent):
    resource_id: UUID
@dataclass(frozen=True)
class GetResourceByTitleEvent(DomainEvent):
    subject_id: UUID
    title: str
