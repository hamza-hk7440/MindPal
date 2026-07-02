from abc import abstractmethod
from ingestion.domain.entities.study_subject_entity import StudySubject
from app.chat.domain.interfaces.base import IRepository
from uuid import UUID

class IStudySubjectRepository(IRepository[StudySubject]):
    @abstractmethod
    async def get_study_subject_by_id(self, study_subject_id: UUID) -> StudySubject | None:
        pass

    @abstractmethod
    async def get_study_subject_by_name(self, user_id: UUID, name: str) -> StudySubject | None:
        pass

    @abstractmethod
    async def save_study_subject(self, study_subject: StudySubject) -> None:
        pass

    @abstractmethod
    async def delete_study_subject(self, study_subject_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_all_study_subjects(self, user_id: UUID) -> list[StudySubject]:
        pass
    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        return await super().exists(entity_id)
    @abstractmethod
    async def update_study_subject(self, study_subject: StudySubject) -> None:
        pass