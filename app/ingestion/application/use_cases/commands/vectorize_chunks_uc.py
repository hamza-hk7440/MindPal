from uuid import UUID
from ingestion.domain.entities.chunks_entity import Chunk
from ingestion.domain.interfaces.chunks_repo import IChunksRepository
from ingestion.domain.events.chunks_events import VectorizeChunkEvent
from ingestion.application.exceptions.exceptions import VectorizationFailureException,ChunkNotFoundException
from chat.domain.interfaces.events import IEventDispatcher
from ingestion.application.services.vectorize_chunk_service import IVectorizeChunkService
from ingestion.domain.entities.chunks_entity import Embedding
from dataclasses import replace as dataclass_replace
class VectorizeChunksUseCase:
    def __init__(
        self,
        chunks_repo: IChunksRepository,
        event_dispatcher: IEventDispatcher,
        vectorize_chunk_service: IVectorizeChunkService
    ):
        self.chunks_repo = chunks_repo
        self.event_dispatcher = event_dispatcher
        self.vectorize_chunk_service = vectorize_chunk_service

    async def _validate_chunk_exists(self, chunk_id: UUID) -> Chunk:
        chunk = await self.chunks_repo.get_chunk_by_id(chunk_id)
        if not chunk:
            raise ChunkNotFoundException(f"Chunk with ID {chunk_id} not found.")
        return chunk

    async def execute(self, chunk_id: UUID, subject_id: UUID) -> None:
        chunk = await self._validate_chunk_exists(chunk_id)
        try:
            # chunk.content is a Value Object; extract raw string
            vector = await self.vectorize_chunk_service.vectorize_chunk(chunk.content.value)
        except Exception as e:
            raise VectorizationFailureException(f"Failed to vectorize chunk {chunk_id}: {str(e)}")

        # Create new Chunk instance with updated embedding
        updated_chunk = Chunk(
            id=chunk.id,
            source_id=chunk.source_id,
            study_subject_id=chunk.study_subject_id,
            content=chunk.content,
            embedding=Embedding(vector),
            created_at=chunk.created_at
        )

        await self.chunks_repo.update_chunk(updated_chunk)
        event = VectorizeChunkEvent(chunk_id=updated_chunk.id, subject_id=subject_id, resource_id=updated_chunk.source_id)
        await self.event_dispatcher.dispatch(event)
