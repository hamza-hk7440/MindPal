from abc import abstractmethod
from app.chat.domain.interfaces.base import IRepository
from uuid import UUID
from ingestion.domain.entities.chunks_entity import Chunk

class IChunksRepository(IRepository[Chunk]):
    @abstractmethod
    async def get_chunk_by_id(self, chunk_id: UUID) -> Chunk | None:
        pass

    @abstractmethod
    async def save_chunk(self, chunk: Chunk) -> None:
        pass

    @abstractmethod
    async def delete_chunk(self, chunk_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_all_chunks(self, resource_id: UUID) -> list[Chunk]:
        pass

    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        return await super().exists(entity_id)