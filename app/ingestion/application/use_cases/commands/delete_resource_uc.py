from ingestion.domain.entities.study_subject_entity import StudySubject
from ingestion.domain.interfaces.study_subject_repo import IStudySubjectRepository
from ingestion.domain.entities.resource_entity import Resource
from ingestion.domain.interfaces.resource_repo import IResourceRepository
from uuid import UUID
from ingestion.domain.events.resource_events import DeleteResourceEvent
from chat.domain.interfaces.events import IEventDispatcher
from ingestion.application.exceptions.exceptions import ResourceNotFoundException, IngestionValidationException

class DeleteResourceUseCase:
    def __init__(self, resource_repo: IResourceRepository, study_subject_repo: IStudySubjectRepository, event_dispatcher: IEventDispatcher):
        self.resource_repo = resource_repo
        self.study_subject_repo = study_subject_repo
        self.event_dispatcher = event_dispatcher
    async def execute(self, resource_id: UUID) -> None:
        # Validate that the resource exists
        resource: Resource | None = await self.resource_repo.get_resource_by_id(resource_id)
        if not resource:
            raise ResourceNotFoundException(f"Resource with ID {resource_id} does not exist.")

        # Validate that the associated study subject exists
        study_subject: StudySubject | None = await self.study_subject_repo.get_study_subject_by_id(resource.subject_id)
        if not study_subject:
            raise IngestionValidationException(f"Study subject with ID {resource.subject_id} does not exist.")

        # Delete the resource
        await self.resource_repo.delete_resource(resource_id)

        # Dispatch an event indicating that the resource has been deleted
        event = DeleteResourceEvent(resource_id=resource_id, subject_id=resource.subject_id)
        await self.event_dispatcher.dispatch(event)