from ingestion.domain.entities.study_subject_entity import StudySubject
from ingestion.domain.interfaces.study_subject_repo import IStudySubjectRepository
from ingestion.application.exceptions.exceptions import StudySubjectNotFoundException
from uuid import UUID
from ingestion.domain.events.study_subject_events import DeleteStudySubjectEvent
from chat.domain.interfaces.events import IEventDispatcher

class DeleteStudySubjectUseCase:
    def __init__(self, study_subject_repo: IStudySubjectRepository, event_dispatcher: IEventDispatcher):
        self.study_subject_repo = study_subject_repo
        self.event_dispatcher = event_dispatcher

    async def execute(self, subject_id: UUID) -> None:
        # Validate that the study subject exists
        study_subject: StudySubject | None = await self.study_subject_repo.get_study_subject_by_id(subject_id)
        if not study_subject:
            raise StudySubjectNotFoundException(f"Study subject with ID {subject_id} does not exist.")

        # Delete the study subject
        await self.study_subject_repo.delete_study_subject(subject_id)

        # Dispatch an event indicating that the study subject has been deleted
        event = DeleteStudySubjectEvent(subject_id)
        await self.event_dispatcher.dispatch(event)