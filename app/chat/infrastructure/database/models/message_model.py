from sqlalchemy import Column, String, DateTime, func, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from enum import Enum
from chat.infrastructure.database.base import Base
from chat.domain.value_objects.message_objects import Role

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    content = Column(String, nullable=False)
    sender = Column(SQLAlchemyEnum(Role), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("ConversationModel", back_populates="messages")