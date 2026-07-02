from abc import abstractmethod
from uuid import UUID
from typing import List, Optional, Tuple

from ingestion.domain.entities.study_subject_entity import StudySubject
from app.chat.domain.interfaces.base import IRepository

class IStudySubjectRepository(IRepository[StudySubject]):
    
    @abstractmethod
    async def get_study_subject_by_id(self, study_subject_id: UUID) -> Optional[StudySubject]:
        pass

    @abstractmethod
    async def get_study_subject_by_name(self, user_id: UUID, name: str) -> Optional[StudySubject]:
        pass

    @abstractmethod
    async def save_study_subject(self, study_subject: StudySubject) -> StudySubject:
        pass

    @abstractmethod
    async def update_study_subject(self, study_subject: StudySubject) -> StudySubject:
        pass

    @abstractmethod
    async def delete_study_subject(self, study_subject_id: UUID, soft_delete: bool = True) -> bool:
        pass

    @abstractmethod
    async def get_all_study_subjects(
        self, 
        user_id: UUID, 
        limit: int = 20, 
        offset: int = 0
    ) -> Tuple[List[StudySubject], int]:
        pass

    @abstractmethod
    async def exists_by_name(self, user_id: UUID, name: str) -> bool:
        pass

    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        pass