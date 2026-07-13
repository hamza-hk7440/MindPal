import redis
import asyncio
from uuid import UUID
from typing import List, Optional
from fastapi import File, UploadFile, Form, APIRouter, Depends, status, WebSocket, WebSocketDisconnect
from ingestion.presentation.schemas.resource_schema import ResourceResponse
from ingestion.presentation.schemas.dependencies import get_resource_controller
from ingestion.presentation.controllers.resource_controller import ResourceController

router = APIRouter(prefix="/resources", tags=["Resources"])
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def add_resource(
    subject_id: UUID = Form(...),
    title: str = Form(...),
    doc_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    controller: ResourceController = Depends(get_resource_controller)
) -> dict:
    resource_dto = await controller.upload_resource(subject_id, title, doc_url, file)
    return {"status": "queued", "task_id": str(resource_dto.id), "resource": resource_dto}

@router.websocket("/tasks/{task_id}")
async def resource_ingestion_progress_ws(task_id: str, websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            progress = r.get(f"task:{task_id}:progress")
            error = r.get(f"task:{task_id}:error")
            
            if error:
                await websocket.send_json({"status": "error", "message": error})
                break
            
            p_val = progress if progress else "0"
            await websocket.send_json({"status": "processing", "progress": p_val})
            
            if p_val == "100":
                break
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(resource_id: UUID, controller: ResourceController = Depends(get_resource_controller)):
    await controller.delete_resource(resource_id)

@router.get("/", response_model=List[ResourceResponse])
async def fetch_all_resources(study_subject_id: UUID = None, controller: ResourceController = Depends(get_resource_controller)):
    return await controller.fetch_all_resources(subject_id=study_subject_id)

@router.post("/ingest", response_model=dict)
async def ingest_resource(
    subject_id: UUID = Form(...),
    title: str = Form(...),
    doc_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    controller: ResourceController = Depends(get_resource_controller)
):
    # Pass them directly to the controller
    return await controller.ingest_resource(
        subject_id=subject_id, 
        title=title, 
        doc_url=doc_url, 
        file=file
    )