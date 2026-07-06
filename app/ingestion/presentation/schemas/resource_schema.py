from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from ingestion.domain.value_objects.type import Doc_type

class AddResourceRequest(BaseModel):
    id: UUID 
    subject_id: UUID
    created_at: datetime
    title: str
    doc_url: str
    doc_type: Doc_type
    content: str
    class Config:
        from_attributes = True
        use_enum_values = True
