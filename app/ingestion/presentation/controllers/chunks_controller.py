from ingestion.presentation.schemas.chunks_schema import Chunk
from ingestion.application.use_cases.commands.split_resources_into_chunks_uc import SplitResourcesIntoChunksUseCase
from ingestion.application.use_cases.commands.vectorize_chunks_uc import VectorizeChunksUseCase
from ingestion.application.use_cases.queries.provide_relevant_chunks_uc import ProvideRelevantChunksUseCase

class ChunksController:
    def __init__(self, split_resources_into_chunks_uc: SplitResourcesIntoChunksUseCase, vectorize_chunks_uc: VectorizeChunksUseCase, provide_relevant_chunks_uc: ProvideRelevantChunksUseCase):
        self.split_resources_into_chunks_uc = split_resources_into_chunks_uc
        self.vectorize_chunks_uc = vectorize_chunks_uc
        self.provide_relevant_chunks_uc = provide_relevant_chunks_uc

    async def split_resources_into_chunks(self, resource_id: str):
        chunks_dto = await self.split_resources_into_chunks_uc.execute(resource_id=resource_id)
        return [Chunk.from_orm(chunk) for chunk in chunks_dto]

    async def vectorize_chunks(self, resource_id: str):
        await self.vectorize_chunks_uc.execute(resource_id=resource_id)

    async def provide_relevant_chunks(self, query: str, subject_id: str):
        relevant_chunks_dto = await self.provide_relevant_chunks_uc.execute(query=query, subject_id=subject_id)
        return [Chunk.from_orm(chunk) for chunk in relevant_chunks_dto]