import base64
from typing import List, Optional
from uuid import UUID
from fastapi import status, HTTPException, UploadFile
from ingestion.presentation.schemas.resource_schema import ResourceResponse
from ingestion.application.use_cases.commands.upload_resource_uc import UploadResourceUseCase
from ingestion.application.use_cases.commands.delete_resource_uc import DeleteResourceUseCase
from ingestion.application.use_cases.queries.fetch_all_resources import FetchAllResourcesUseCase
from ingestion.application.exceptions.exceptions import (
    ResourceNotFoundException,
    ExtractionFailureException,
    UnsupportedResourceFormatException
)

class ResourceController:
    def __init__(
        self, 
        upload_resource_uc: UploadResourceUseCase, 
        delete_resource_uc: DeleteResourceUseCase, 
        fetch_all_resources_uc: FetchAllResourcesUseCase,
        ingest_resource_task
    ):
        self._upload_uc = upload_resource_uc
        self._delete_uc = delete_resource_uc
        self._fetch_all_uc = fetch_all_resources_uc
        self._ingest_task = ingest_resource_task  

    async def upload_resource(
        self,
        subject_id: UUID,
        title: str,
        doc_url: Optional[str],
        file: Optional[UploadFile]
    ) -> ResourceResponse:
        try:
            file_bytes = await file.read() if file else None
            resource_dto = await self._upload_uc.execute(
                subject_id=subject_id,
                title=title,
                doc_url=doc_url,
                file_bytes=file_bytes,
                file=file,
            )
            return ResourceResponse.model_validate(resource_dto)
        except UnsupportedResourceFormatException as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        except ExtractionFailureException as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    async def delete_resource(self, resource_id: UUID) -> None:
        try:
            await self._delete_uc.execute(resource_id=resource_id)
        except ResourceNotFoundException as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    async def fetch_all_resources(self, subject_id: UUID) -> List[ResourceResponse]:
        resources_dto = await self._fetch_all_uc.execute(subject_id=subject_id)
        return [ResourceResponse.model_validate(r) for r in resources_dto]

    async def ingest_resource(self, subject_id: UUID, title: str, doc_url: Optional[str], file: Optional[UploadFile]):
        file_bytes = await file.read() if file else None
        file_bytes_encoded = base64.b64encode(file_bytes).decode('utf-8') if file_bytes else None
        
        task = self._ingest_task.delay(
            subject_id=str(subject_id), 
            title=title, 
            doc_url=doc_url, 
            file_bytes=file_bytes_encoded
        )
        return {"task_id": task.id}