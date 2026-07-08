from typing import List
from uuid import UUID
from fastapi import status, HTTPException

# Presentation Layer Schema Context
from ingestion.presentation.schemas.chunks_schema import Chunk
# Application Layer Use Case Contracts
from ingestion.application.use_cases.commands.split_resources_into_chunks_uc import SplitResourcesIntoChunksUseCase
from ingestion.application.use_cases.commands.vectorize_chunks_uc import VectorizeChunksUseCase
from ingestion.application.use_cases.queries.provide_relevant_chunks_uc import ProvideRelevantChunksUseCase
# Application Layer Structural Exception Boundaries
from ingestion.application.exceptions.exceptions import (
    ResourceNotFoundException,
    IngestionExternalServiceException,  # For Vector DB or Embedding API failures
    IngestionValidationException
)

class ChunksController:
    def __init__(
        self, 
        split_resources_into_chunks_uc: SplitResourcesIntoChunksUseCase, 
        vectorize_chunks_uc: VectorizeChunksUseCase, 
        provide_relevant_chunks_uc: ProvideRelevantChunksUseCase
    ):
        self._split_uc = split_resources_into_chunks_uc
        self._vectorize_uc = vectorize_chunks_uc
        self._provide_relevant_uc = provide_relevant_chunks_uc

    async def split_resources_into_chunks(self, resource_id: UUID, study_subject_id: UUID) -> List[Chunk]:
        """
        Retrieves a text resource asset and processes it through the text-splitting engine.
        """
        try:
            chunks_dto = await self._split_uc.execute(resource_id=resource_id, study_subject_id=study_subject_id)
            return [Chunk.model_validate(chunk) for chunk in chunks_dto]
            
        except ResourceNotFoundException as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc)
            )
        except IngestionValidationException as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Text splitting failed due to invalid structural input: {str(exc)}"
            )

    async def vectorize_chunks(self, resource_id: UUID) -> None:
        """
        Generates vector embeddings for a resource's chunks and upserts them to the vector store.
        """
        try:
            await self._vectorize_uc.execute(resource_id=resource_id)
            
        except ResourceNotFoundException as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc)
            )
        except IngestionExternalServiceException as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Vector store or Embedding API dependency down: {str(exc)}"
            )

    async def provide_relevant_chunks(self, query: str, subject_id: UUID) -> List[Chunk]:
        """
        Executes a semantic vector similarity search across documents mapped to a specific subject context.
        """
        try:
            relevant_chunks_dto = await self._provide_relevant_uc.execute(
                query=query, 
                subject_id=subject_id
            )
            return [Chunk.model_validate(chunk) for chunk in relevant_chunks_dto]
            
        except IngestionExternalServiceException as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Semantic search failed on downstream vector store index lookup: {str(exc)}"
            )