from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class Chunk(BaseModel):
    id: UUID
    resource_id: UUID
    study_subject_id: UUID
    content: str
    embedding: list[float]
    created_at: datetime

    class Config:
        from_attributes = True