from uuid import UUID
from ingestion.domain.entities.chunks_entity import Chunk
from ingestion.domain.interfaces.chunks_repo import IChunksRepository
from ingestion.domain.events.chunks_events import GetRelevantChunksEvent
from chat.domain.interfaces.events import IEventDispatcher
from ingestion.application.exceptions.exceptions import IngestionExternalServiceException,IngestionProcessFailureException
from ingestion.application.services.execute_vector_search_service import IExecuteVectorSearchService
from ingestion.application.services.vectorize_chunk_service import IVectorizeChunkService
class ProvideRelevantChunksUseCase:
    def __init__(
        self,
        chunks_repo: IChunksRepository,
        event_dispatcher: IEventDispatcher,
        execute_vector_search_service: IExecuteVectorSearchService,
        vectorize_chunk_service: IVectorizeChunkService
    ):
        self.chunks_repo = chunks_repo
        self.event_dispatcher = event_dispatcher
        self.execute_vector_search_service = execute_vector_search_service
        self.vectorize_chunk_service = vectorize_chunk_service

    async def execute(self, query:str,threshold:float,count:int,filter_subject_id:UUID) -> list[Chunk]:
        try:
            query_vector = await self.vectorize_chunk_service.vectorize_chunk(query)
        except Exception as e:
            raise IngestionProcessFailureException(f"Failed to vectorize query: {str(e)}")
        try:
            search_results = await self.execute_vector_search_service.execute_vector_search(query_vector, threshold, count, filter_subject_id)
        except Exception as e:
            raise IngestionExternalServiceException(f"Failed to execute vector search: {str(e)}")
        
        event = GetRelevantChunksEvent(query=query,subject_id=filter_subject_id)
        await self.event_dispatcher.dispatch(event)
        return search_results
