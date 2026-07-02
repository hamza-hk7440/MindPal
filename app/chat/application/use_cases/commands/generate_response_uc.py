from chat.domain.interfaces.rag_provider import IRAGProvider
from chat.domain.entities.message import ChatMessage
from chat.domain.events.messages_events import SendMessageEvent
from chat.domain.interfaces.message_repo import IMessageRepository
from chat.domain.interfaces.events import IEventDispatcher
from chat.domain.value_objects.message_objects import Role
from chat.application.services.gemini_service import IGeminiService
from chat.application.services.llama2_service import ILlama2Service
from chat.application.exceptions.exception import InvalidMessageException,ConversationNotFoundException
from chat.application.dtos.message_dto import SendMessageDTO
from chat.domain.interfaces.conversation_repo import IConversationRepository
from chat.infrastructure.config.settings import settings
from chat.application.use_cases.queries.fetch_message import FetchMessageUseCase
from uuid import UUID


class GenerateResponseUseCase:
    def __init__(
        self,
        message_repo: IMessageRepository,
        gemini_service: IGeminiService,
        llama2_service: ILlama2Service,
        conversation_repo: IConversationRepository,
        event_dispatcher: IEventDispatcher,
        rag_provider: IRAGProvider
    ):
        self.message_repo = message_repo
        self.gemini_service = gemini_service
        self.llama2_service = llama2_service
        self.conversation_repo = conversation_repo
        self.event_dispatcher = event_dispatcher
        self.rag_provider = rag_provider
    async def _validate_message_input(self , content: str, sender: Role, conversation_id: UUID) -> None:
        if not content or content.strip() == "":
            raise InvalidMessageException("Message content cannot be empty.")
        if not isinstance(sender, Role):
            raise InvalidMessageException("Sender must be a valid Role.")
        # Check if the conversation exists
        conversation_exists = await self.conversation_repo.exists(conversation_id)
        if not conversation_exists:
            raise ConversationNotFoundException(f"Conversation with ID {conversation_id} does not exist.")

    async def _generate_ai_response(self,chunks: list[str], conversation_id: UUID, content: str, chat_history: list) -> str:
        
        if settings.USE_LOCAL_LLM or settings.ENVIRONMENT.lower() == "local":
            return await self.llama2_service.send_message_to_llama2(chunks, conversation_id, content, chat_history)

        return await self.gemini_service.send_message_to_gemini(chunks, conversation_id, content, chat_history)

    async def generate_response(self, conversation_id: UUID, content: str)-> SendMessageDTO:
        await self._validate_message_input(content, Role.AI, conversation_id)
        chat_history = await FetchMessageUseCase(self.message_repo, self.event_dispatcher, self.conversation_repo).fetch_messages_by_conversation_id(conversation_id)
        chunks = await self.rag_provider.get_context_chunks(content)
        response_content = await self._generate_ai_response(chunks, conversation_id, content, chat_history=chat_history)
        # Create the response message entity
        response_message = ChatMessage.create(conversation_id=conversation_id, content=response_content, sender=Role.AI)
        # Save the response message using the repository
        await self.message_repo.save_message(response_message)
        # Publish the SendMessageEvent for the response
        event = SendMessageEvent(
            message_id=response_message.id,
            conversation_id=response_message.conversation_id,
            content=response_message.content.value,
            sender=response_message.sender
        )
        await self.event_dispatcher.dispatch(event)
        # Return a DTO representation of the response message
        return SendMessageDTO(
            id=response_message.id,
            conversation_id=response_message.conversation_id,
            content=response_message.content.value,
            sender=response_message.sender,
            created_at=response_message.created_at
        )
