from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from ingestion.domain.value_objects.type import Doc_type

class AddResourceRequest(BaseModel):
    id: UUID 
    subject_id: UUID
    created_at: datetime
    title: str
    doc_url: Optional[str]= None
    doc_type: Doc_type
    content: Optional[str]= None
    class Config:
        from_attributes = True
        use_enum_values = True
class ResourceResponse(BaseModel):
    id: UUID
    subject_id: UUID
    created_at: Optional[datetime]
    title: str
    doc_url: Optional[str]= None
    doc_type: Doc_type
    content: Optional[str]= None
    class Config:
        from_attributes = True
        use_enum_values = True