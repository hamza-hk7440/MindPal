from typing import List
from uuid import UUID
from ingestion.domain.entities.chunks_entity import Chunk
from ingestion.application.dtos.chunks_dto import ChunkDTO
from fastapi import status, HTTPException

from ingestion.application.use_cases.commands.split_resources_into_chunks_uc import SplitResourcesIntoChunksUseCase
from ingestion.application.use_cases.commands.vectorize_chunks_uc import VectorizeChunksUseCase
from ingestion.application.use_cases.queries.provide_relevant_chunks_uc import ProvideRelevantChunksUseCase
from ingestion.application.use_cases.commands.delete_chunk_by_subject_id_uc import DeleteChunkBySubjectIdUseCase
from ingestion.application.use_cases.commands.delete_chunk_by_resource_uc import DeleteChunkByResourceUseCase 
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
        provide_relevant_chunks_uc: ProvideRelevantChunksUseCase,
        delete_chunk_by_subject_id_uc: DeleteChunkBySubjectIdUseCase,
        delete_chunk_by_resource_uc: DeleteChunkByResourceUseCase
    ):
        self._split_uc = split_resources_into_chunks_uc
        self._vectorize_uc = vectorize_chunks_uc
        self._provide_relevant_uc = provide_relevant_chunks_uc
        self._delete_by_subject_uc = delete_chunk_by_subject_id_uc
        self._delete_by_resource_uc = delete_chunk_by_resource_uc

    async def split_resources_into_chunks(self, resource_id: UUID, study_subject_id: UUID) -> List[dict]:
        try:
            chunks = await self._split_uc.execute(resource_id=resource_id, study_subject_id=study_subject_id)            
            return [chunk.model_dump() for chunk in chunks]
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

    async def provide_relevant_chunks(self, query: str, subject_id: UUID) -> List[dict]:
        try:
            raw_data = await self._provide_relevant_uc.execute(
                query=query, 
                threshold=0.3,
                count=2,
                filter_subject_id=subject_id
            )
            
            entities = [Chunk.from_db_dict(item) for item in raw_data]
            
            return [ChunkDTO.from_entity(entity).model_dump() for entity in entities]
            
        except IngestionExternalServiceException as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc)
            )
    async def delete_chunks_by_resource(self, resource_id: UUID) -> None:
        """
        Deletes all chunks associated with a given resource ID.
        """
        try:
            await self._delete_by_resource_uc.execute(resource_id=resource_id)
        except ResourceNotFoundException as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc)
            )
    async def delete_chunks_by_study_subject(self, study_subject_id: UUID) -> None:
        """
        Deletes all chunks associated with a given study subject ID.
        """
        try:
            await self._delete_by_subject_uc.execute(study_subject_id=study_subject_id)
        except ResourceNotFoundException as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc)
            )