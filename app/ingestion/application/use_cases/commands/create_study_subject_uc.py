from ingestion.domain.entities.study_subject_entity import StudySubject
from ingestion.domain.events.study_subject_events import CreateStudySubjectEvent
from ingestion.domain.interfaces.study_subject_repo import IStudySubjectRepository
from chat.domain.interfaces.events import IEventDispatcher
from ingestion.application.dtos.study_subject_dto import CreateStudySubjectDTO
from uuid import UUID

class CreateStudySubjectUseCase:
    def __init__(self, study_subject_repo: IStudySubjectRepository, event_dispatcher: IEventDispatcher):
        self.study_subject_repo = study_subject_repo
        self.event_dispatcher = event_dispatcher

    async def _validate_study_subject_input(self, user_id: UUID, name: str) -> None:
        if not name or name.strip() == "":
            raise ValueError("Study subject name cannot be empty.")
        # Check if the study subject already exists for the user
        existing_subject = await self.study_subject_repo.get_study_subject_by_name(user_id, name)
        if existing_subject:
            raise ValueError(f"Study subject with name '{name}' already exists for user {user_id}.")
    async def create_study_subject(self, user_id: UUID, name: str) -> CreateStudySubjectDTO:
        await self._validate_study_subject_input(user_id, name)
        # Create the study subject entity
        study_subject = StudySubject.create(user_id=user_id, name=name)
        # Save the study subject using the repository
        await self.study_subject_repo.save_study_subject(study_subject)
        # Publish the CreateStudySubjectEvent
        event = CreateStudySubjectEvent(
            study_subject_id=study_subject.id,
            user_id=study_subject.user_id,
            name=study_subject.name
        )
        await self.event_dispatcher.dispatch(event)
        # Return a DTO representation of the study subject
        return CreateStudySubjectDTO(
            id=study_subject.id,
            user_id=study_subject.user_id,
            name=study_subject.name,
            created_at=study_subject.created_at
        )
    async def execute(self, user_id: UUID, name: str) -> CreateStudySubjectDTO:
        return await self.create_study_subject(user_id, name)
        