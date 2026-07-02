from uuid import UUID

from chat.domain.interfaces.events import IEventDispatcher
from chat.domain.interfaces.message_repo import IMessageRepository
from chat.domain.interfaces.conversation_repo import IConversationRepository
from chat.application.exceptions.exception import ConversationNotFoundException
from chat.domain.events.messages_events import GetAllMessagesEvent
class FetchMessageUseCase:
    def __init__(self, message_repo: IMessageRepository, event_dispatcher: IEventDispatcher, conversation_repo: IConversationRepository):
        self.message_repo = message_repo
        self.conversation_repo = conversation_repo
        self.event_dispatcher = event_dispatcher

    async def fetch_messages_by_conversation_id(self, conversation_id: UUID, skip: int = 0, limit: int = 100):
        # Check if the conversation exists
        conversation_exists = await self.conversation_repo.conversation_exists(conversation_id)
        if not conversation_exists:
            raise ConversationNotFoundException(f"Conversation with ID {conversation_id} does not exist.")
        # Fetch messages from the repository
        messages = await self.message_repo.get_messages_by_conversation_id(conversation_id, skip, limit)
        # Optionally, you can dispatch an event here if needed
        event = GetAllMessagesEvent(conversation_id=conversation_id)
        await self.event_dispatcher.dispatch(event)
        return messages