from abc import ABC, abstractmethod
class IVectorizeChunkService(ABC):
    @abstractmethod
    async def vectorize_chunk(self, chunk: str) -> list[float]:
        pass