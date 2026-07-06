from ingestion.presentation.schemas.resource_schema import AddResourceRequest
from ingestion.application.use_cases.commands.upload_resource_uc import UploadResourceUseCase
from ingestion.application.use_cases.commands.delete_resource_uc import DeleteResourceUseCase
from ingestion.application.use_cases.queries.fetch_all_resources import FetchAllResourcesUseCase

class ResourceController:
    def __init__(self, upload_resource_uc: UploadResourceUseCase, delete_resource_uc: DeleteResourceUseCase, fetch_all_resources_uc: FetchAllResourcesUseCase):
        self.upload_resource_uc = upload_resource_uc
        self.delete_resource_uc = delete_resource_uc
        self.fetch_all_resources_uc = fetch_all_resources_uc
    async  def upload_resource(self, request: AddResourceRequest):
        resource_dto = await self.upload_resource_uc.execute(
            id=request.id,
            subject_id=request.subject_id,
            created_at=request.created_at,
            title=request.title,
            doc_url=request.doc_url,
            doc_type=request.doc_type,
            content=request.content
        )
        return resource_dto
    async def delete_resource(self, resource_id: str):
        await self.delete_resource_uc.execute(resource_id=resource_id)
    async def fetch_all_resources(self, subject_id: str):
        resources_dto = await self.fetch_all_resources_uc.execute(subject_id=subject_id)
        return [resource for resource in resources_dto]
    