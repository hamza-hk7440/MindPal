from uuid import UUID
from fastapi import File,UploadFile,Form,APIRouter, Depends, status, WebSocket, WebSocketDisconnect
from typing import List,Optional
import asyncio
# Presentation Schema Context
from ingestion.presentation.schemas.resource_schema import AddResourceRequest
# Dependency Injection Components
from ingestion.presentation.schemas.dependencies import get_resource_controller
from ingestion.presentation.controllers.resource_controller import ResourceController

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.post(
    "/", 
    status_code=status.HTTP_202_ACCEPTED,
    summary="Initiate resource upload and text extraction pipeline"
)
async def add_resource(
    subject_id: UUID = Form(...),
    title: str = Form(...),
    doc_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    controller: ResourceController = Depends(get_resource_controller)
) -> dict:
    resource_dto = await controller.upload_resource(
        subject_id=subject_id,
        title=title,
        doc_url=doc_url,
        file=file
    )
    
    return {
        "status": "queued",
        "message": "Resource ingestion started successfully.",
        "task_id": str(resource_dto.id),
        "resource": resource_dto
    }


@router.websocket("/tasks/{task_id}")
async def resource_ingestion_progress_ws(task_id: UUID, websocket: WebSocket):
    """
    Live WebSocket endpoint to let front-end UI components track file ingestion 
    and extraction pipeline stages in real time without holding up HTTP requests.
    """
    await websocket.accept()
    try:
        # Pipeline execution steps example
        # Production tip: Bind this loop to a Redis Pub/Sub channel or Celery/Task state manager keyed by task_id
        pipeline_stages = [
            {"step": "downloading_binary_payload", "progress_pct": 20},
            {"step": "evaluating_file_mime_type", "progress_pct": 40},
            {"step": "extracting_raw_text_via_ai_engines", "progress_pct": 75},
            {"step": "structural_chunking_and_token_indexing", "progress_pct": 90},
            {"step": "pipeline_completed", "progress_pct": 100}
        ]

        for stage in pipeline_stages:
            await websocket.send_json({
                "task_id": str(task_id),
                "status": "processing" if stage["progress_pct"] < 100 else "completed",
                "stage": stage["step"],
                "progress": stage["progress_pct"]
            })
            # Simulate processing delay intervals between pipeline layers
            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        # Safeguard clean socket termination if user navigates away or loses connection
        pass


@router.delete(
    "/{resource_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resource asset"
)
async def delete_resource(
    resource_id: UUID, 
    controller: ResourceController = Depends(get_resource_controller)
) -> None:
    await controller.delete_resource(resource_id)


@router.get(
    "/{resource_id}", 
    response_model=dict,
    summary="Fetch a specific resource asset details"
)
async def fetch_resource(
    resource_id: UUID, 
    controller: ResourceController = Depends(get_resource_controller)
) -> dict:
    return await controller.fetch_resource(resource_id)


@router.get(
    "/", 
    response_model=List[dict],
    summary="Fetch all ingested resources"
)
async def fetch_all_resources(
    controller: ResourceController = Depends(get_resource_controller)
) -> List[dict]:
    return await controller.fetch_all_resources()


@router.get(
    "/study-subject/{study_subject_id}", 
    response_model=List[dict],
    summary="Fetch resources bound to a specific study subject"
)
async def fetch_resources_by_study_subject(
    study_subject_id: UUID, 
    controller: ResourceController = Depends(get_resource_controller)
) -> List[dict]:
    return await controller.fetch_all_resources(subject_id=study_subject_id)


@router.get(
    "/user/{user_id}", 
    response_model=List[dict],
    summary="Fetch resources created by a specific user"
)
async def fetch_resources_by_user(
    user_id: UUID, 
    controller: ResourceController = Depends(get_resource_controller)
) -> List[dict]:
    return await controller.fetch_resources_by_user(user_id)