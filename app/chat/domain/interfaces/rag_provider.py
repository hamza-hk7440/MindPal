from abc import ABC, abstractmethod

class IRAGProvider(ABC):
    @abstractmethod
    async def get_context_chunks(self, query: str) -> list[str]:
        pass