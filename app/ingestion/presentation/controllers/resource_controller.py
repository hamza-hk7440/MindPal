from typing import List
from uuid import UUID
from fastapi import status, HTTPException

# Presentation Layer Schema Context
from ingestion.presentation.schemas.resource_schema import AddResourceRequest, ResourceResponse
# Application Layer Use Case Contracts
from ingestion.application.use_cases.commands.upload_resource_uc import UploadResourceUseCase
from ingestion.application.use_cases.commands.delete_resource_uc import DeleteResourceUseCase
from ingestion.application.use_cases.queries.fetch_all_resources import FetchAllResourcesUseCase
# Application Layer Structural Exception Boundaries
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
        fetch_all_resources_uc: FetchAllResourcesUseCase
    ):
        self._upload_uc = upload_resource_uc
        self._delete_uc = delete_resource_uc
        self._fetch_all_uc = fetch_all_resources_uc

    async def upload_resource(self, request: AddResourceRequest) -> ResourceResponse:
        """
        Coordinates the orchestration payload for uploading and parsing an asset.
        Catches background extraction engine failures gracefully.
        """
        try:
            resource_dto = await self._upload_uc.execute(
                id=request.id,
                subject_id=request.subject_id,
                created_at=request.created_at,
                title=request.title,
                doc_url=request.doc_url,
                doc_type=request.doc_type,
                content=request.content
            )
            return ResourceResponse.model_validate(resource_dto)
            
        except UnsupportedResourceFormatException as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc)
            )
        except ExtractionFailureException as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Resource processing pipeline failed: {str(exc)}"
            )

    async def delete_resource(self, resource_id: UUID) -> None:
        """
        Dispatches target ID coordinates to delete an ingested resource asset.
        """
        try:
            await self._delete_uc.execute(resource_id=resource_id)
            
        except ResourceNotFoundException as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc)
            )

    async def fetch_all_resources(self, subject_id: UUID) -> List[ResourceResponse]:
        """
        Queries application read layers to gather all resources grouped under a subject.
        """
        resources_dto = await self._fetch_all_uc.execute(subject_id=subject_id)
        
        return [
            ResourceResponse.model_validate(resource) 
            for resource in resources_dto
        ]