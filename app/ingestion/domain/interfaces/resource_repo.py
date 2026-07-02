from abc import abstractmethod
from app.chat.domain.interfaces.base import IRepository
from uuid import UUID
from ingestion.domain.entities.resource_entity import Resource

class IResourceRepository(IRepository[Resource]):
    @abstractmethod
    async def get_resource_by_id(self, resource_id: UUID) -> Resource | None:
        pass

    @abstractmethod
    async def save_resource(self, resource: Resource) -> None:
        pass

    @abstractmethod
    async def delete_resource(self, resource_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_all_resources(self, subject_id: UUID) -> list[Resource]:
        pass

    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        return await super().exists(entity_id)
    @abstractmethod
    async def get_resources_by_title(self, subject_id: UUID, title: str) -> list[Resource]:
        pass