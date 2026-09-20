from datetime import datetime
from uuid import UUID

from supabase import AsyncClient

from chat.domain.entities.message import ChatMessage, Content
from chat.domain.interfaces.message_repo import IMessageRepository
from chat.domain.value_objects.message_objects import Role
from chat.infrastructure.config.settings import settings


class MessageRepository(IMessageRepository):
    _local_rows: dict[str, dict] = {}

    def __init__(self, client: AsyncClient):
        self.client = client
        self.table_name = settings.SUPABASE_MESSAGES_TABLE

    def _table(self):
        return self.client.table(self.table_name)

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def _parse_role(value: str) -> Role:
        return Role(value)

    @staticmethod
    def _serialize_role(role: Role) -> str:
        return role.value

    @classmethod
    def _to_entity(cls, row: dict) -> ChatMessage:
        return ChatMessage(
            conversation_id=UUID(str(row["conversation_id"])),
            content=Content(row["content"]),
            sender=cls._parse_role(str(row["sender"])),
            id=UUID(str(row["id"])),
            created_at=cls._parse_datetime(row.get("created_at")),
        )

    async def get_message_by_id(self, message_id: UUID) -> ChatMessage | None:
        try:
            response = await (
                self._table()
                .select("*")
                .eq("id", str(message_id))
                .limit(1)
                .execute()
            )
            rows = response.data or []
            if not rows:
                return None
            return self._to_entity(rows[0])
        except Exception:
            row = self._local_rows.get(str(message_id))
            return self._to_entity(row) if row else None

    async def save_message(self, message: ChatMessage) -> None:
        row = {
            "id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "content": message.content.value,
            "sender": self._serialize_role(message.sender),
            "created_at": message.created_at.isoformat() if message.created_at else None,
        }
        try:
            await self._table().insert(row).execute()
        except Exception:
            self._local_rows[row["id"]] = row

    async def get_all_messages_by_conversation_id(self, conversation_id: UUID) -> list[ChatMessage]:
        try:
            response = await (
                self._table()
                .select("*")
                .eq("conversation_id", str(conversation_id))
                .order("created_at")
                .execute()
            )
            return [self._to_entity(row) for row in response.data or []]
        except Exception:
            rows = [row for row in self._local_rows.values() if str(row.get("conversation_id")) == str(conversation_id)]
            rows.sort(key=lambda row: row.get("created_at") or "")
            return [self._to_entity(row) for row in rows]

    async def get_messages_by_conversation_id(self, conversation_id: UUID, skip: int = 0, limit: int = 100) -> list[ChatMessage]:
        try:
            response = await (
                self._table()
                .select("*")
                .eq("conversation_id", str(conversation_id))
                .order("created_at")
                .range(skip, skip + limit - 1)
                .execute()
            )
            return [self._to_entity(row) for row in response.data or []]
        except Exception:
            rows = [row for row in self._local_rows.values() if str(row.get("conversation_id")) == str(conversation_id)]
            rows.sort(key=lambda row: row.get("created_at") or "")
            rows = rows[skip : skip + limit]
            return [self._to_entity(row) for row in rows]

    async def exists(self, entity_id: UUID) -> bool:
        try:
            response = await (
                self._table()
                .select("id")
                .eq("id", str(entity_id))
                .limit(1)
                .execute()
            )
            return bool(response.data)
        except Exception:
            return str(entity_id) in self._local_rows

    async def add(self, entity: ChatMessage) -> None:
        await self.save_message(entity)

    async def get(self, entity_id: UUID) -> ChatMessage | None:
        return await self.get_message_by_id(entity_id)

    async def update(self, entity: ChatMessage) -> None:
        try:
            await (
                self._table()
                .update(
                    {
                        "content": entity.content.value,
                        "sender": self._serialize_role(entity.sender),
                    }
                )
                .eq("id", str(entity.id))
                .execute()
            )
        except Exception:
            existing = self._local_rows.get(str(entity.id))
            if existing:
                existing["content"] = entity.content.value
                existing["sender"] = self._serialize_role(entity.sender)

    async def delete(self, entity_id: UUID) -> None:
        try:
            await self._table().delete().eq("id", str(entity_id)).execute()
        except Exception:
            self._local_rows.pop(str(entity_id), None)