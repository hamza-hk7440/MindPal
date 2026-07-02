from chat.domain.events.conversation_event import ConversationCreatedEvent
from chat.domain.interfaces.conversation_repo import IConversationRepository
from chat.application.exceptions.exception import ConversationCreationFailureException
from chat.domain.interfaces.events import IEventDispatcher
from chat.application.dtos.conversation_dto import ConversationDTO
from chat.domain.entities.conversation import Conversation
from uuid import UUID
class CreateConversationUseCase:
    def __init__(self, conversation_repo: IConversationRepository, event_dispatcher: IEventDispatcher):
        self.conversation_repo = conversation_repo
        self.event_dispatcher = event_dispatcher

    async def create_conversation(self, subject_id: UUID) -> ConversationDTO:
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
