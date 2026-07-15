from uuid import UUID
from fastapi import APIRouter, Depends, status
from ingestion.presentation.schemas.dependencies import get_chunks_controller
from ingestion.presentation.controllers.chunks_controller import ChunksController
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from ingestion.infrastructure.tasks import r
router = APIRouter(prefix="/chunks", tags=["Chunks Ingestion"])

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def add_chunk(study_subject_id: UUID, resource_id: UUID, controller: ChunksController = Depends(get_chunks_controller)):
    return await controller.split_resources_into_chunks(resource_id=resource_id, study_subject_id=study_subject_id)
@router.websocket("/ws/task/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    try:
        while True:
            progress = r.get(f"task:{task_id}:progress")
            error = r.get(f"task:{task_id}:error")
            
            if error:
                await websocket.send_json({"status": "error", "message": error.decode()})
                break            
            await websocket.send_json({"progress": progress.decode() if progress else "0"})
            if progress and progress.decode() == "100":
                break
                
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass