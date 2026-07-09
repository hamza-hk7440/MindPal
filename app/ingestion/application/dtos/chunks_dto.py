from datetime import datetime
from typing import Annotated
from uuid import UUID
from ingestion.domain.entities.chunks_entity import Chunk
from pydantic import BaseModel, Field, ConfigDict

class ChunkDTO(BaseModel):
    id: Annotated[UUID, Field(description="The unique identifier of the chunk.")]
    resource_id: Annotated[UUID, Field(description="The ID of the associated resource.")]
    study_subject_id: Annotated[UUID, Field(description="The ID of the associated study subject.")]
    content: Annotated[str, Field(min_length=1, max_length=10000)]
    embedding: Annotated[list[float], Field(description="The embedding vector for the chunk.")]
    created_at: Annotated[datetime | None, Field(description="The timestamp when the chunk was created.")] = None
    model_config=ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat() 
        },
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
    @classmethod
    def from_entity(cls, chunk_entity: Chunk) -> "ChunkDTO":
        # 1. Force content to string
        raw_content = chunk_entity.content.value if hasattr(chunk_entity.content, 'value') else str(chunk_entity.content)
        
        # 2. Force embedding to a plain Python list[float]
        emb_obj = chunk_entity.embedding
        if hasattr(emb_obj, 'values'):
            raw_embedding = list(emb_obj.values)
        elif hasattr(emb_obj, '_values'):
            raw_embedding = list(emb_obj._values)
        else:
            raw_embedding = list(emb_obj) # Fallback to trying to cast whatever it is to a list

        return cls(
            id=chunk_entity.id,
            resource_id=chunk_entity.source_id,
            study_subject_id=chunk_entity.study_subject,
            content=raw_content,
            embedding=raw_embedding,
            created_at=chunk_entity.created_at
        )