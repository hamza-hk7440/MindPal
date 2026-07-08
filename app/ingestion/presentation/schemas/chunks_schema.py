from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class Chunk(BaseModel):
    id: UUID
    source_id: UUID
    study_subject: UUID
    content: str
    embedding: list[float]
    created_at: datetime

    class Config:
        from_attributes = True