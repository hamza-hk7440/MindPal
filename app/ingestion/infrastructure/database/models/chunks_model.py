from sqlalchemy import Column, String, DateTime, func, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from pgvector.sqlalchemy import Vector
from app.chat.infrastructure.database.base import Base

class ChunkModel(Base):
    __tablename__="Chunks"
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id=Column(UUID(as_uuid=True), ForeignKey("Sources.id"), nullable=False)
    study_subject_id=Column(UUID(as_uuid=True), ForeignKey("Study_subject.id"), nullable=False) 
    content=Column(String, nullable=False)
    created_at=Column(DateTime, default=func.now())
    embedding=Column(Vector(1536), nullable=False)  # Assuming embedding is a vector of floats with a fixed size of 1536