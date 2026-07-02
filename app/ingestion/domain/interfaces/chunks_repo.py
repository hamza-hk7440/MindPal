from abc import abstractmethod
from uuid import UUID
from typing import List, Optional, Tuple

from ingestion.domain.entities.chunks_entity import Chunk
from app.chat.domain.interfaces.base import IRepository

class IChunksRepository(IRepository[Chunk]):
    
    @abstractmethod
    async def get_chunk_by_id(self, chunk_id: UUID) -> Optional[Chunk]:
        pass

    @abstractmethod
    async def save_chunk(self, chunk: Chunk) -> Chunk:
        pass

    @abstractmethod
    async def save_chunks_batch(self, chunks: List[Chunk]) -> List[Chunk]:
        pass

    @abstractmethod
    async def delete_chunk(self, chunk_id: UUID) -> bool:
        pass

    @abstractmethod
    async def delete_all_chunks_by_resource(self, resource_id: UUID) -> int:
        pass

    @abstractmethod
    async def get_all_chunks(
        self, 
        resource_id: UUID, 
        limit: int = 50, 
        offset: int = 0
    ) -> Tuple[List[Chunk], int]:
        pass