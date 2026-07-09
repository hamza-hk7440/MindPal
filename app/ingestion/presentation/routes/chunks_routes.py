from uuid import UUID
from fastapi import APIRouter, Depends, status
from typing import List
from ingestion.application.dtos.chunks_dto import ChunkDTO
from ingestion.presentation.schemas.chunks_schema import Chunk
from ingestion.presentation.schemas.dependencies import get_chunks_controller
from ingestion.presentation.controllers.chunks_controller import ChunksController

router = APIRouter(prefix="/chunks", tags=["Chunks Ingestion"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=List[ChunkDTO])
async def add_chunk(study_subject_id: UUID, resource_id: UUID, controller: ChunksController = Depends(get_chunks_controller)):
    return await controller.split_resources_into_chunks(resource_id=resource_id, study_subject_id=study_subject_id)
@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chunk(chunk_id: UUID, controller: ChunksController = Depends(get_chunks_controller)):
    await controller.delete_chunk(chunk_id)

@router.get("/{chunk_id}", response_model=dict)
async def fetch_chunk(chunk_id: UUID, controller: ChunksController = Depends(get_chunks_controller)):
    return await controller.fetch_chunk(chunk_id)

@router.get("/", response_model=List[dict])
async def fetch_all_chunks(controller: ChunksController = Depends(get_chunks_controller)):
    return await controller.fetch_all_chunks()

@router.get("/resource/{resource_id}", response_model=List[dict])
async def fetch_chunks_by_resource(resource_id: UUID, controller: ChunksController = Depends(get_chunks_controller)):
    return await controller.fetch_chunks_by_resource(resource_id)
@router.get("/study-subject/{subject_id}", response_model=List[dict])
async def provide_relevant_chunks(subject_id: UUID, query: str, controller: ChunksController = Depends(get_chunks_controller)):
    return await controller.provide_relevant_chunks(subject_id=subject_id, query=query)