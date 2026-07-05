from ingestion.application.services.vectorize_chunk_service import IVectorizeChunkService
from google import genai
genai.configure(api_key="GEMINI_API_KEY")
client=genai.Client(api_key="GEMINI_API_KEY")
class VectorizeChunkService(IVectorizeChunkService):
    async def vectorize_chunk(self, chunk: str) -> list[float]:
        
        response = client.models.embed_content(
            model="gemini-embedding-2",
            content=chunk
        )
        return response.embedding[0].values
    