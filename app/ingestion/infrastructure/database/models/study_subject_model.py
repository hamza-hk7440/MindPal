from sqlalchemy import Column, String, DateTime, func, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.chat.infrastructure.database.base import Base

class StudySubjectModel(Base):
    __tablename__="Study_subject"
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id=Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name=Column(String, nullable=False)
    created_at=Column(DateTime, default=func.now())
    