from ingestion.domain.entities.study_subject_entity import StudySubject
from ingestion.domain.interfaces.study_subject_repo import IStudySubjectRepository
from ingestion.domain.entities.resource_entity import Resource
from ingestion.domain.interfaces.resource_repo import IResourceRepository
from uuid import UUID
from ingestion.domain.events.resource_events import GetAllResourcesEvent
from chat.domain.interfaces.events import IEventDispatcher
class FetchAllResourcesUseCase:
    def __init__(self, resource_repo: IResourceRepository, study_subject_repo: IStudySubjectRepository, event_dispatcher: IEventDispatcher):
        self.resource_repo = resource_repo
        self.study_subject_repo = study_subject_repo
        self.event_dispatcher = event_dispatcher

    async def execute(self, subject_id: UUID) -> list[Resource]:
        # Validate that the study subject exists
        study_subject: StudySubject | None = await self.study_subject_repo.get_study_subject_by_id(subject_id)
        if not study_subject:
            from ingestion.application.exceptions.exceptions import IngestionValidationException
            raise IngestionValidationException(f"Study subject with ID {subject_id} does not exist.")

        # Fetch all resources for the given study subject
        resources, _ = await self.resource_repo.get_all_resources(subject_id)

        # Dispatch an event indicating that all resources have been fetched
        event = GetAllResourcesEvent(subject_id=subject_id)
        await self.event_dispatcher.dispatch(event)

        return resources