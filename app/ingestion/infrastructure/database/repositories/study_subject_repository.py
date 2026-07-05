from datetime import datetime
from uuid import UUID
from supabase import AsyncClient

from ingestion.domain.entities.study_subject_entity import StudySubject, Name

from ingestion.domain.interfaces.study_subject_repo import IStudySubjectRepository
from app.chat.infrastructure.config.settings import settings

class StudySubjectRepository(IStudySubjectRepository):
    def __init__(self, client: AsyncClient):
        self.client = client
        self.table_name = settings.SUPABASE_STUDY_SUBJECTS_TABLE

    def _table(self):
        return self.client.table(self.table_name)

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @classmethod
    def _to_entity(cls, row: dict) -> StudySubject:
        return StudySubject(
            id=UUID(str(row["id"])),
            user_id=UUID(str(row["user_id"])),
            name=Name(row["name"]),
            created_at=cls._parse_datetime(row.get("created_at")),
        )

    async def get_study_subject_by_id(self, study_subject_id: UUID) -> StudySubject | None:
        response = await (
            self._table()
            .select("*")
            .eq("id", str(study_subject_id))
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        return self._to_entity(rows[0])

    async def get_study_subject_by_name(self, user_id: UUID, name: str) -> StudySubject | None:
        response = await (
            self._table()
            .select("*")
            .eq("user_id", str(user_id))
            .eq("name", name)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        return self._to_entity(rows[0])

    async def save_study_subject(self, study_subject: StudySubject) -> None:
        await (
            self._table()
            .insert(
                {
                    "id": str(study_subject.id),
                    "user_id": str(study_subject.user_id),
                    "name": study_subject.name.value,
                    "created_at": study_subject.created_at.isoformat() if study_subject.created_at else None,
                }
            )
            .execute()
        )

    async def get_all_study_subjects(self, user_id: UUID, limit: int = 20, offset: int = 0) -> tuple[list[StudySubject], int]:
        response = await (
            self._table()
            .select("*", count="exact")
            .eq("user_id", str(user_id))
            .limit(limit)
            .offset(offset)
            .execute()
        )
        rows = response.data or []
        total_count = response.count or 0
        return [self._to_entity(row) for row in rows], total_count
    
    async def update_study_subject(self, study_subject: StudySubject) -> None:
        await (
            self._table()
            .update(
                {
                    "name": study_subject.name.value,
                }
            )
            .eq("id", str(study_subject.id))
            .execute()
        )

    async def delete_study_subject(self, study_subject_id: UUID) -> None:
        await (
            self._table()
            .delete()
            .eq("id", str(study_subject_id))
            .execute()
        )
    async def exists_by_name(self, user_id: UUID, name: str) -> bool:
        response = await (
            self._table()
            .select("id")
            .eq("user_id", str(user_id))
            .eq("name", name)
            .limit(1)
            .execute()
        )

        rows = response.data or []
        return len(rows) > 0
    async def exists(self, entity_id: UUID) -> bool:
        response = await (
            self._table()
            .select("id")
            .eq("id", str(entity_id))
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return len(rows) > 0