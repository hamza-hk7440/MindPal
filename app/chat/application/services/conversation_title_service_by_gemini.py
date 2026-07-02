from abc import ABC, abstractmethod

class IConversationTitleServiceByGemini(ABC):
    @abstractmethod
    async def generate_conversation_title_by_gemini(self, message: str) -> str:
        pass