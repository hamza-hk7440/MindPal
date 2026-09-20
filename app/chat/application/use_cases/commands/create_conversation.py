from chat.domain.events.conversation_event import ConversationCreatedEvent
from chat.domain.interfaces.conversation_repo import IConversationRepository
from chat.application.exceptions.exception import ConversationCreationFailureException
from chat.domain.interfaces.events import IEventDispatcher
from chat.application.dtos.conversation_dto import ConversationDTO
from chat.domain.entities.conversation import Conversation
from ingestion.domain.interfaces.study_subject_repo import IStudySubjectRepository
from uuid import UUID
class CreateConversationUseCase:
    def __init__(
        self,
        conversation_repo: IConversationRepository,
        event_dispatcher: IEventDispatcher,
        study_subject_repo: IStudySubjectRepository | None = None,
    ):
        self.conversation_repo = conversation_repo
        self.event_dispatcher = event_dispatcher
        self.study_subject_repo = study_subject_repo

    async def create_conversation(self, subject_id: UUID) -> ConversationDTO:
        if self.study_subject_repo and not await self.study_subject_repo.exists(subject_id):
            raise ConversationCreationFailureException(f"Study subject with ID {subject_id} does not exist.")

        subject_title = f"Subject {subject_id}"
        conversation = Conversation(id=None, title=subject_title, subject_id=subject_id)
        await self.conversation_repo.save_conversation(conversation)
        if not conversation.id:
            raise ConversationCreationFailureException("Failed to create a new conversation.")
        
        # Publish the ConversationCreatedEvent
        event = ConversationCreatedEvent(conversation_id=conversation.id, subject_id=subject_id, title=subject_title)
        await self.event_dispatcher.dispatch(event)

        # Return a DTO representation of the created conversation
        return ConversationDTO(id=conversation.id, title=conversation.title, subject_id=subject_id)
