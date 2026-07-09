from datetime import datetime
from uuid import UUID
from supabase import AsyncClient
from ingestion.domain.entities.resource_entity import Resource
from ingestion.domain.interfaces.resource_repo import IResourceRepository
from chat.infrastructure.config.settings import settings
from ingestion.domain.value_objects.type import Doc_type

class ResourceRepository(IResourceRepository):
    def __init__(self, client: AsyncClient):
        self.client = client
        self.table_name = settings.SUPABASE_RESOURCES_TABLE

   

    # Added @staticmethod to remove 'self' positional tracking requirements
    
    # Explicitly declared as a proper classmethod matching your invocation pattern
    @classmethod
    def _to_entity(cls, row: dict) -> Resource:
        return Resource(
            id=UUID(str(row["id"])),
            subject_id=UUID(str(row["subject_id"])),
            title=row["title"],
            content=row.get("content"),
            doc_type=Doc_type(row.get("doc_type")),
            created_at=cls._parse_datetime(row.get("created_at")),
            doc_url=row.get("doc_url"),
        )

    # Added self parameter to match instance invocation context safely
    def _serialize_type(self, doc_type: Doc_type) -> str:
        return doc_type.value

    async def get_resource_by_id(self, resource_id: UUID) -> Resource | None:
        response = await (
            self._table()
            .select("*")
            .eq("id", str(resource_id))
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        return self._to_entity(rows[0])
    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    async def save_resource(self, resource: Resource) -> Resource:
        # Unpack Domain Value Objects into primitive types before upserting
        data = {
            "id": str(resource.id),
            "subject_id": str(resource.subject_id),
            "title": resource.title.value if hasattr(resource.title, "value") else str(resource.title),
            "doc_url": resource.doc_url.value if hasattr(resource.doc_url, "value") else str(resource.doc_url),
            "doc_type": resource.doc_type.value if hasattr(resource.doc_type, "value") else str(resource.doc_type),
            "content": resource.content.value if hasattr(resource.content, "value") else str(resource.content),
            "created_at": resource.created_at.isoformat() if hasattr(resource.created_at, "isoformat") else resource.created_at
        }

        await self._table().upsert(data).execute()
        return resource
    async def update_resource(self, resource: Resource) -> None:
        data = {
            "subject_id": str(resource.subject_id),
            "title": resource.title,
            "content": resource.content,
            "type": self._serialize_type(resource.doc_type),
        }
        await self._table().update(data).eq("id", str(resource.id)).execute()

    async def delete_resource(self, resource_id: UUID, soft_delete: bool = True) -> bool:

        response = await self._table().delete().eq("id", str(resource_id)).execute()
        # Check standard truthiness/length of data rather than raw HTTP client code strings
        return bool(response.data)

    async def get_all_resources(
        self, 
        subject_id: UUID, 
        limit: int = 20, 
        offset: int = 0
    ) -> tuple[list[Resource], int]:
        response = await (
            self._table()
            .select("*", count="exact")
            .eq("subject_id", str(subject_id))
            .limit(limit)
            .offset(offset)
            .execute()
        )
        rows = response.data or []
        total_count = response.count or 0
        resources = [self._to_entity(row) for row in rows]
        return resources, total_count

    async def get_resources_by_title(
        self, 
        subject_id: UUID, 
        title: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> tuple[list[Resource], int]:
        response = await (
            self._table()
            .select("*", count="exact")
            .eq("subject_id", str(subject_id))
            .ilike("title", f"%{title}%")
            .limit(limit)
            .offset(offset)
            .execute()
        )
        rows = response.data or []
        total_count = response.count or 0
        resources = [self._to_entity(row) for row in rows]
        return resources, total_count

    async def exists_by_title(self, subject_id: UUID, title: str) -> bool:
        response = await (
            self._table()
            .select("id")
            .eq("subject_id", str(subject_id))
            .eq("title", title)
            .limit(1)
            .execute()
        )
        return bool(response.data)

    async def exists(self, entity_id: UUID) -> bool:
        response = await (
            self._table()
            .select("id")
            .eq("id", str(entity_id))
            .limit(1)
            .execute()
        )
        return bool(response.data)
    def _table(self):
        return self.client.table(self.table_name)
    async def get_content_by_resource_id(self, resource_id: UUID) -> str | None:
        response = await (
            self._table()
            .select("content")
            .eq("id", str(resource_id))
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        return rows[0].get("content")
    async def add(self, resource: Resource) -> None:
        await self.save_resource(resource)
    async def get(self, entity_id: UUID) -> Resource | None:
        return await self.get_resource_by_id(entity_id)
    async def update(self, resource: Resource) -> None:
        await self.update_resource(resource)
    async def delete(self, entity_id: UUID) -> None:
        await self.delete_resource(entity_id, soft_delete=True)