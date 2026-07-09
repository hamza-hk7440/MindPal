from uuid import UUID
from fastapi import APIRouter, Depends, status
from typing import List
from ingestion.application.dtos.chunks_dto import ChunkDTO
from ingestion.presentation.schemas.dependencies import get_chunks_controller
from ingestion.presentation.controllers.chunks_controller import ChunksController

router = APIRouter(prefix="/chunks", tags=["Chunks Ingestion"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=List[ChunkDTO])
async def add_chunk(study_subject_id: UUID, resource_id: UUID, controller: ChunksController = Depends(get_chunks_controller)):
    return await controller.split_resources_into_chunks(resource_id=resource_id, study_subject_id=study_subject_id)
@router.get("/study-subject/{subject_id}", response_model=List[dict])
async def provide_relevant_chunks(subject_id: UUID, query: str, controller: ChunksController = Depends(get_chunks_controller)):
    return await controller.provide_relevant_chunks(subject_id=subject_id, query=query)
@router.post("/deletechunkbyresource/{resource_id}", status_code=status.HTTP_200_OK)
async def delete_chunks_by_resource(resource_id: UUID, controller: ChunksController = Depends(get_chunks_controller)):
    await controller.delete_chunks_by_resource(resource_id=resource_id)
    return {"message": f"Chunks associated with resource {resource_id} have been deleted."}
@router.post("/deletechunkbystudysubject/{study_subject_id}", status_code=status.HTTP_200_OK)
async def delete_chunks_by_study_subject(study_subject_id: UUID, controller: ChunksController = Depends(get_chunks_controller)):
    await controller.delete_chunks_by_study_subject(study_subject_id=study_subject_id)
    return {"message": f"Chunks associated with study subject {study_subject_id} have been deleted."}