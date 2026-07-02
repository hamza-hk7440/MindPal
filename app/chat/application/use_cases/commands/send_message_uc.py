from chat.domain.entities.message import ChatMessage
from chat.domain.events.messages_events import SendMessageEvent
from chat.domain.interfaces.message_repo import IMessageRepository
from chat.domain.interfaces.events import IEventDispatcher
from chat.domain.value_objects.message_objects import Role
from chat.application.services.gemini_service import IGeminiService
from chat.application.exceptions.exception import InvalidMessageException,ConversationNotFoundException
from chat.application.dtos.message_dto import SendMessageDTO
from uuid import UUID
from chat.domain.interfaces.conversation_repo import IConversationRepository
class SendMessageUseCase:
    def __init__(self, message_repo: IMessageRepository, message_service: IGeminiService, conversation_repo: IConversationRepository, event_dispatcher: IEventDispatcher):
        self.message_repo = message_repo
        self.message_service = message_service
        self.conversation_repo = conversation_repo
        self.event_dispatcher = event_dispatcher

    @staticmethod
    def _normalize_sender(sender: Role | str) -> Role:
        if isinstance(sender, Role):
            return sender
        return Role(str(sender))

    async def _validate_message_input(self, content: str, sender: Role | str, conversation_id: UUID) -> Role:
        if not content or content.strip() == "":
            raise InvalidMessageException("Message content cannot be empty.")
        try:
            normalized_sender = self._normalize_sender(sender)
        except ValueError as exc:
            raise InvalidMessageException("Sender must be a valid Role.") from exc
        # Check if the conversation exists
        conversation_exists = await self.conversation_repo.exists(conversation_id)
        if not conversation_exists:
            raise ConversationNotFoundException(f"Conversation with ID {conversation_id} does not exist.")
        return normalized_sender

    async def send_message(self, conversation_id: UUID, content: str, sender: Role | str) -> SendMessageDTO:
        # Validate input
        sender = await self._validate_message_input(content, sender, conversation_id)
        # Create the message entity
        message = ChatMessage(conversation_id=conversation_id, content=content, sender=sender)
        # Save the message using the repository
        await self.message_repo.save_message(message)
        # Publish the SendMessageEvent
        event = SendMessageEvent(
            message_id=message.id,
            conversation_id=message.conversation_id,
            content=message.content,
            sender=message.sender
        )
        await self.event_dispatcher.dispatch(event)
        # Return a DTO representation of the message
        return SendMessageDTO(
            id=message.id,
            conversation_id=message.conversation_id,
            content=message.content,
            sender=message.sender,
            created_at=message.created_at
        )

    async def execute(self, conversation_id: UUID, content: str, sender: Role | str) -> SendMessageDTO:
        return await self.send_message(conversation_id, content, sender)
    