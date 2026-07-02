from abc import ABC, abstractmethod
class ILlama2Service(ABC):
    @abstractmethod
    async def send_message_to_llama2(self, cleaned_context: str, conversation_id: str, message: str) -> str:
        pass