from uuid import UUID
from fastapi import APIRouter, Depends, status
from typing import List

from ingestion.presentation.schemas.chunks_schema import Chunk
from ingestion.presentation.schemas.dependencies import get_chunks_controller
from ingestion.presentation.controllers.chunks_controller import ChunksController

router = APIRouter(prefix="/chunks", tags=["Chunks Ingestion"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_chunk(chunk: Chunk, controller: ChunksController = Depends(get_chunks_controller)):
    return await controller.add_chunk(chunk)

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