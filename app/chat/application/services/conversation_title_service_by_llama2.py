from abc import ABC, abstractmethod

class IConversationTitleServiceByLlama2(ABC):
    @abstractmethod
    async def generate_conversation_title_by_llama2(self, message: str) -> str:
        pass