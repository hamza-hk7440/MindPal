from uuid import UUID
from ingestion.domain.entities.resource_entity import Resource
from ingestion.domain.interfaces.resource_repo import IResourceRepository
from ingestion.domain.entities.chunks_entity import Chunk
from ingestion.domain.interfaces.chunks_repo import IChunksRepository
from ingestion.domain.events.chunks_events import SplitChunkEvent
from chat.domain.interfaces.events import IEventDispatcher
from ingestion.application.services.slice_document_into_chunks_service import ISliceDocumentIntoChunksService
from ingestion.application.services.vectorize_chunk_service import IVectorizeChunkService
from ingestion.application.exceptions.exceptions import ResourceNotFoundException, ChunkingFailureException
from ingestion.domain.interfaces.study_subject_repo import IStudySubjectRepository
from ingestion.application.dtos.chunks_dto import ChunkDTO
class SplitResourcesIntoChunksUseCase:
    def __init__(
        self,
        resource_repo: IResourceRepository,
        chunks_repo: IChunksRepository,
        event_dispatcher: IEventDispatcher,
        slice_document_service: ISliceDocumentIntoChunksService,
        study_subject_repo: IStudySubjectRepository,
        vectorize_chunk_service: IVectorizeChunkService
    ):
        self.resource_repo = resource_repo
        self.chunks_repo = chunks_repo
        self.event_dispatcher = event_dispatcher
        self.slice_document_service = slice_document_service
        self.study_subject_repo = study_subject_repo
        self.vectorize_chunk_service = vectorize_chunk_service

    async def _validate_resource_exists(self, resource_id: UUID) -> Resource:
        resource = await self.resource_repo.get_resource_by_id(resource_id)
        if not resource:
            raise ResourceNotFoundException(f"Resource with ID {resource_id} not found.")
        return resource

    async def execute(self, resource_id: UUID, study_subject_id: UUID) -> list[ChunkDTO]:
        resource = await self._validate_resource_exists(resource_id)
        try:
            chunks_content = await self.slice_document_service.slice_document_into_chunks(resource.content)
        except Exception as e:
            raise ChunkingFailureException(f"Failed to chunk resource {resource_id}: {str(e)}")
        
        processed_chunks = []
        for content in chunks_content:
            embedding_vector = await self.vectorize_chunk_service.vectorize_chunk(content)
            
            chunk = Chunk.create(
                source_id=resource.id, 
                study_subject=study_subject_id, 
                content=content, 
                embedding=embedding_vector
            )
            
            await self.chunks_repo.save_chunk(chunk)
            
            event = SplitChunkEvent(
                chunk_id=chunk.id, 
                subject_id=study_subject_id, 
                resource_id=resource_id
            )
            await self.event_dispatcher.dispatch(event)
            
            processed_chunks.append(ChunkDTO.from_entity(chunk))
            
        return processed_chunks