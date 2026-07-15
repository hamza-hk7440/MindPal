from uuid import UUID
from typing import List
from fastapi import status, HTTPException
from ingestion.application.use_cases.commands.split_resources_into_chunks_uc import SplitResourcesIntoChunksUseCase
from ingestion.infrastructure.tasks import process_chunks_task

class ChunksController:
    def __init__(self, split_resources_into_chunks_uc, vectorize_chunks_uc, provide_relevant_chunks_uc, delete_chunk_by_subject_id_uc, delete_chunk_by_resource_uc):
        self._split_uc = split_resources_into_chunks_uc
        self._vectorize_uc = vectorize_chunks_uc
        self._provide_relevant_uc = provide_relevant_chunks_uc
        self._delete_by_subject_uc = delete_chunk_by_subject_id_uc
        self._delete_by_resource_uc = delete_chunk_by_resource_uc

    async def split_resources_into_chunks(self, resource_id: UUID, study_subject_id: UUID) -> dict:
        task = process_chunks_task.delay(str(resource_id), str(study_subject_id))
        return {"task_id": task.id}

    async def vectorize_chunks(self, resource_id: UUID) -> None:
        await self._vectorize_uc.execute(resource_id=resource_id)

    async def provide_relevant_chunks(self, query: str, subject_id: UUID) -> List[dict]:
        return await self._provide_relevant_uc.execute(query=query, threshold=0.3, count=2, filter_subject_id=subject_id)

    async def delete_chunks_by_resource(self, resource_id: UUID) -> None:
        await self._delete_by_resource_uc.execute(resource_id=resource_id)

    async def delete_chunks_by_study_subject(self, study_subject_id: UUID) -> None:
        await self._delete_by_subject_uc.execute(study_subject_id=study_subject_id)