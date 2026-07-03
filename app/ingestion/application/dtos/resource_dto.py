from datetime import datetime
from typing import Annotated
from uuid import UUID
from ingestion.domain.value_objects.type import Doc_type 
from pydantic import BaseModel, Field, ConfigDict

class AddResourceDTO(BaseModel):
    id: Annotated[UUID, Field(description="The resource ID.")]
    subject_id: Annotated[UUID, Field(description="The ID of the associated study subject.")]
    created_at: Annotated[datetime | None, Field(description="The timestamp when the resource was created.")] = None
    title: Annotated[str, Field(min_length=1, max_length=255)]
    doc_url: Annotated[str, Field(min_length=1, max_length=2048)]
    doc_type: Annotated[Doc_type, Field(description="The type of the document (e.g., PDF, Video, etc.).")]
    content: Annotated[str, Field(min_length=1, max_length=10000, description="The extracted content of the resource.")]
    model_config=ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "12345678-1234-5678-1234-567812345678",
                "subject_id": "22345678-1234-5678-1234-567812345678",
                "created_at": "2026-07-01T08:45:26.210381",
                "title": "Calculus Notes",
                "doc_url": "https://example.com/resources/calculus_notes.pdf",
                "doc_type": "PDF",
                "content": "This is the extracted content of the calculus notes."
            }
        }
    )
    