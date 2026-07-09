import logging
from ingestion.application.services.vectorize_chunk_service import IVectorizeChunkService
from google import genai
from google.genai import errors
from chat.infrastructure.config.settings import settings

class VectorizationError(Exception):
    pass

class VectorizeChunkService(IVectorizeChunkService):
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY) 
        self._model = "gemini-embedding-2"
        self.logger = logging.getLogger(__name__)

    async def vectorize_chunk(self, chunk: str) -> list[float]:
        try:
            response = self.client.models.embed_content(
                model=self._model,
                contents=chunk
            )
            
            if not response.embeddings:
                raise VectorizationError("No embeddings returned from Gemini")
                
            return response.embeddings[0].values
            
        except errors.APIError as exc:
            self.logger.error(f"Gemini API failure: {exc}")
            raise VectorizationError(f"Failed to vectorize: {str(exc)}")
        except Exception as exc:
            self.logger.exception("Unexpected error in vectorization")
            raise VectorizationError("An internal error occurred during vectorization")