from ingestion.domain.entities.study_subject_entity import StudySubject
from ingestion.domain.interfaces.study_subject_repo import IStudySubjectRepository
from ingestion.application.exceptions.exceptions import StudySubjectNotFoundException
from uuid import UUID
from ingestion.domain.events.study_subject_events import GetStudySubjectByIdEvent,GetAllStudySubjectsEvent
from chat.domain.interfaces.events import IEventDispatcher
class FetchStudySubjectUseCase:
    def __init__(self, study_subject_repo: IStudySubjectRepository, event_dispatcher: IEventDispatcher):
        self.study_subject_repo = study_subject_repo
        self.event_dispatcher = event_dispatcher

    async def fetch_one_study_subject(self, subject_id: UUID) -> StudySubject:
        study_subject = await self.study_subject_repo.get_study_subject_by_id(subject_id)
        event = GetStudySubjectByIdEvent(subject_id)
        await self.event_dispatcher.dispatch(event)
        if not study_subject:
            raise StudySubjectNotFoundException(f"Study subject with ID {subject_id} not found.")
        return study_subject
    async def fetch_all_study_subjects(self, user_id: UUID) -> list[StudySubject]:
        event = GetAllStudySubjectsEvent(user_id=user_id)
        await self.event_dispatcher.dispatch(event)
        study_subjects = await self.study_subject_repo.get_all_study_subjects(user_id=user_id)
        return study_subjects