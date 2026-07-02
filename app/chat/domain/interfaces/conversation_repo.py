from abc import abstractmethod
from chat.domain.entities.conversation import Conversation
from chat.domain.interfaces.base import IRepository
from uuid import UUID

class IConversationRepository(IRepository[Conversation]):
    @abstractmethod
    async def get_conversation_by_id(self, conversation_id: UUID) -> Conversation | None:
        pass

    @abstractmethod
    async def get_conversations_by_subject_id(self, subject_id: UUID, skip: int = 0, limit: int = 100) -> list[Conversation]:
        pass

    @abstractmethod
    async def save_conversation(self, conversation: Conversation) -> None:
        pass
    @abstractmethod
    async def conversation_exists(self, entity_id: UUID) -> bool:
        pass

