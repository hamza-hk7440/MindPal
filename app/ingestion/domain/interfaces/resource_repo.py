from abc import abstractmethod
from uuid import UUID
from typing import List, Optional, Tuple

from ingestion.domain.entities.resource_entity import Resource
from app.chat.domain.interfaces.base import IRepository

class IResourceRepository(IRepository[Resource]):
    
    @abstractmethod
    async def get_resource_by_id(self, resource_id: UUID) -> Optional[Resource]:
        pass

    @abstractmethod
    async def save_resource(self, resource: Resource) -> Resource:
        pass

    @abstractmethod
    async def update_resource(self, resource: Resource) -> Resource:
        pass

    @abstractmethod
    async def delete_resource(self, resource_id: UUID, soft_delete: bool = True) -> bool:
        pass

    @abstractmethod
    async def get_all_resources(
        self, 
        subject_id: UUID, 
        limit: int = 20, 
        offset: int = 0
    ) -> Tuple[List[Resource], int]:
        pass

    @abstractmethod
    async def get_resources_by_title(
        self, 
        subject_id: UUID, 
        title: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> Tuple[List[Resource], int]:
        pass

    @abstractmethod
    async def exists_by_title(self, subject_id: UUID, title: str) -> bool:
        pass

    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        pass
    @abstractmethod
    async def get_content_by_resource_id(self, resource_id: UUID) -> Optional[str]:
        pass