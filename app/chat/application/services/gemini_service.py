from abc import ABC, abstractmethod

class  IGeminiService(ABC):
    @abstractmethod
    async def send_message_to_gemini(self,cleaned_context: str, conversation_id: str, message: str) -> str:
        pass

