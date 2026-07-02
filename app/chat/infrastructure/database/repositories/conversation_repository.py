from datetime import datetime
from uuid import UUID

from supabase import AsyncClient

from chat.domain.entities.conversation import Conversation
from chat.domain.interfaces.conversation_repo import IConversationRepository
from chat.infrastructure.config.settings import settings


class ConversationRepository(IConversationRepository):
    def __init__(self, client: AsyncClient):
        self.client = client
        self.table_name = settings.SUPABASE_CONVERSATIONS_TABLE

    def _table(self):
        return self.client.table(self.table_name)

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @classmethod
    def _to_entity(cls, row: dict) -> Conversation:
        return Conversation(
            id=UUID(str(row["id"])),
            subject_id=UUID(str(row["subject_id"])),
            title=row["title"],
            created_at=cls._parse_datetime(row.get("created_at")),
        )

    async def get_conversation_by_id(self, conversation_id: UUID) -> Conversation | None:
        response = await (
            self._table()
            .select("*")
            .eq("id", str(conversation_id))
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        return self._to_entity(rows[0])

    async def get_conversations_by_subject_id(
        self,
        subject_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Conversation]:
        response = await (
            self._table()
            .select("*")
            .eq("subject_id", str(subject_id))
            .order("created_at")
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [self._to_entity(row) for row in response.data or []]

    async def save_conversation(self, conversation: Conversation) -> None:
        await (
            self._table()
            .insert(
                {
                    "id": str(conversation.id),
                    "subject_id": str(conversation.subject_id),
                    "title": conversation.title,
                }
            )
            .execute()
        )

    async def conversation_exists(self, entity_id: UUID) -> bool:
        response = await (
            self._table()
            .select("id")
            .eq("id", str(entity_id))
            .limit(1)
            .execute()
        )
        return bool(response.data)

    async def exists(self, entity_id: UUID) -> bool:
        return await self.conversation_exists(entity_id)

    async def add(self, entity: Conversation) -> None:
        await self.save_conversation(entity)

    async def get(self, entity_id: UUID) -> Conversation | None:
        return await self.get_conversation_by_id(entity_id)

    async def update(self, entity: Conversation) -> None:
        await (
            self._table()
            .update(
                {
                    "subject_id": str(entity.subject_id),
                    "title": entity.title,
                }
            )
            .eq("id", str(entity.id))
            .execute()
        )

    async def delete(self, entity_id: UUID) -> None:
        await self._table().delete().eq("id", str(entity_id)).execute()
