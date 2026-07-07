from ingestion.application.services.vectorize_chunk_service import IVectorizeChunkService
from google import genai
from fastapi import status, HTTPException
from google.genai import errors
from chat.infrastructure.config.settings import settings
class VectorizeChunkService(IVectorizeChunkService):
    def __init__(self):
        self.client =genai.Client(api_key=settings.GEMINI_API_KEY) 
        self._model="text-embedding-004"

    async def vectorize_chunk(self, chunk: str) -> list[float]:
        try:
            response = self.client.models.embed_content(
                model=self._model,
                content=chunk
            )
            return response.embedding[0].values
        except errors.APIError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"gemini api vectorization error: {exc}",
            )