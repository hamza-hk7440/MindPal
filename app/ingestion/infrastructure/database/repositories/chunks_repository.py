from datetime import datetime
from uuid import UUID
from supabase import AsyncClient
from ingestion.domain.entities.chunks_entity import Chunk
from ingestion.domain.interfaces.chunks_repo import IChunksRepository
from app.chat.infrastructure.config.settings import settings

class ChunksRepository(IChunksRepository):
    def __init__(self, client: AsyncClient):
        self.client = client
        self.table_name = settings.SUPABASE_CHUNKS_TABLE

    def _table(self):
        return self.client.table(self.table_name)

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @classmethod
    def _to_entity(cls, row: dict) -> Chunk:
        return Chunk(
            id=UUID(str(row["id"])),
            resource_id=UUID(str(row["resource_id"])),
            content=row.get("content"),
            created_at=cls._parse_datetime(row.get("created_at")),
        )
    async def get_chunk_by_id(self, chunk_id: UUID) -> Chunk | None:
        response = await (
            self._table()
            .select("*")
            .eq("id", str(chunk_id))
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        return self._to_entity(rows[0])
    async def save_chunk(self, chunk: Chunk) -> None:
        data = {
            "id": str(chunk.id),
            "resource_id": str(chunk.resource_id),
            "content": chunk.content,
            "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
        }
        await self._table().upsert(data).execute()
    async def save_chunks_batch(self, chunks: list[Chunk]) -> None:
        data = [
            {
                "id": str(chunk.id),
                "resource_id": str(chunk.resource_id),
                "content": chunk.content,
                "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
            }
            for chunk in chunks
        ]
        await self._table().upsert(data).execute()
    async def delete_chunk(self, chunk_id: UUID) -> bool:
        response = await self._table().delete().eq("id", str(chunk_id)).execute()
        return response.status_code == 200
    async def delete_all_chunks_by_resource(self, resource_id: UUID) -> int:
        response = await self._table().delete().eq("resource_id", str(resource_id)).execute()
        return len(response.data or [])
    async def get_all_chunks(
        self, 
        resource_id: UUID, 
        limit: int = 50, 
        offset: int = 0
    ) -> tuple[list[Chunk], int]:
        response = await (
            self._table()
            .select("*", count="exact")
            .eq("resource_id", str(resource_id))
            .limit(limit)
            .offset(offset)
            .execute()
        )
        rows = response.data or []
        total_count = response.count or 0
        chunks = [self._to_entity(row) for row in rows]
        return chunks, total_count
    async def update_chunk(self, chunk: Chunk) -> None:
        data = {
            "resource_id": str(chunk.resource_id),
            "content": chunk.content,
        }
        await self._table().update(data).eq("id", str(chunk.id)).execute()
        