from dataclasses import dataclass
from uuid import UUID
from app.chat.domain.events.base import DomainEvent

@dataclass(frozen=True)
class CreateStudySubjectEvent(DomainEvent):
    study_subject_id: UUID
    user_id: UUID
    name: str
@dataclass(frozen=True)
class UpdateStudySubjectEvent(DomainEvent):
    study_subject_id: UUID
    user_id: UUID
    name: str

@dataclass(frozen=True)
class DeleteStudySubjectEvent(DomainEvent):
    study_subject_id: UUID
    user_id: UUID
@dataclass(frozen=True)
class GetAllStudySubjectsEvent(DomainEvent):
    user_id: UUID
@dataclass(frozen=True)
class GetStudySubjectEvent(DomainEvent):
    study_subject_id: UUID
    user_id: UUID
@dataclass(frozen=True)
class GetStudySubjectByNameEvent(DomainEvent):
    user_id: UUID
    name: str
@dataclass(frozen=True)
class GetStudySubjectByIdEvent(DomainEvent):
    study_subject_id: UUID
    user_id: UUID
