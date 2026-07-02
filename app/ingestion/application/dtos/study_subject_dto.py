from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

class CreateStudySubjectDTO(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]
    created_at: Annotated[datetime | None, Field(description="The timestamp when the study subject was created.")] = None
    model_config=ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "Mathematics",
                "created_at": "2026-07-01T08:45:26.210381"
            }
        }
    )
class StudySubjectDTO(BaseModel):
    id: Annotated[UUID, Field(description="The unique identifier of the study subject.")]
    name: Annotated[str, Field(min_length=1, max_length=255)]
    created_at: Annotated[datetime | None, Field(description="The timestamp when the study subject was created.")] = None
    model_config=ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "id": "12345678-1234-5678-1234-567812345678",
                "name": "Mathematics",
                "created_at": "2026-07-01T08:45:26.210381"
            }
        }
    )
