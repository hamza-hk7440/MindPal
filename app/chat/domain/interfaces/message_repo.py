from abc import abstractmethod
from chat.domain.entities.message import ChatMessage
from chat.domain.interfaces.base import IRepository
from uuid import UUID
class IMessageRepository(IRepository[ChatMessage]):
    @abstractmethod
    async def get_message_by_id(self, message_id: UUID) -> ChatMessage | None:
        pass
    @abstractmethod
    async def get_messages_by_conversation_id(self, conversation_id: UUID, skip: int = 0, limit: int = 100) -> list[ChatMessage]:
        pass
    @abstractmethod
    async def save_message(self, message: ChatMessage) -> None:
        pass
    @abstractmethod
    async def get_all_messages_by_conversation_id(self, conversation_id: UUID) -> list[ChatMessage]:
        pass
    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        return await super().exists(entity_id)