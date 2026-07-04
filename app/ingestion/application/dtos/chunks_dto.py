from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

class ChunkDTO(BaseModel):
    id: Annotated[UUID, Field(description="The unique identifier of the chunk.")]
    resource_id: Annotated[UUID, Field(description="The ID of the associated resource.")]
    study_subject_id: Annotated[UUID, Field(description="The ID of the associated study subject.")]
    content: Annotated[str, Field(min_length=1, max_length=10000)]
    embedding: Annotated[list[float], Field(description="The embedding vector for the chunk.")]
    created_at: Annotated[datetime | None, Field(description="The timestamp when the chunk was created.")] = None
    model_config=ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "12345678-1234-5678-1234-567812345678",
                "resource_id": "12345678-1234-5678-1234-567812345678",
                "content": "This is a sample chunk of text from the resource.",
                "created_at": "2026-07-01T08:45:26.210381"
            }
        }
    )