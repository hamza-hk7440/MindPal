from sqlalchemy import Column, String, DateTime, func, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.chat.infrastructure.database.base import Base
from ingestion.domain.value_objects.type import Doc_type

class ResourceModel(Base):
    __tablename__ = "Sources"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("Study_subject.id"), nullable=False)
    title = Column(String, nullable=False)
    content=Column(String, nullable=False)
    doc_url=Column(String, nullable=False)
    doc_type=Column(SQLAlchemyEnum(Doc_type), nullable=False)
    created_at = Column(DateTime, default=func.now())