from typing import List, Optional
from uuid import UUID

from chromadb import logger
from fastapi import status, HTTPException,UploadFile

# Presentation Layer Schema Context
from ingestion.presentation.schemas.resource_schema import  ResourceResponse
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

    async def upload_resource(
        self,
        subject_id: UUID,
        title: str,
        doc_url: Optional[str],
        file: Optional[UploadFile]
    ) -> ResourceResponse:
        try:
            file_bytes = None
            if file:
                file_bytes = await file.read() 
                if not title:
                    title = file.filename

            resource_dto = await self._upload_uc.execute(
                subject_id=subject_id,
                title=title,
                doc_url=doc_url,
                file_bytes=file_bytes,
                file=file,
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
        except Exception as exc:
            logger.error(f"Unhandled systemic exception during resource upload: {str(exc)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal structural error occurred while executing the transaction."
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