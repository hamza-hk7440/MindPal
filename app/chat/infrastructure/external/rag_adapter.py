from chat.domain.interfaces.rag_provider import IRAGProvider
from app.assessment.services import RAGService

class RAGAdapter(IRAGProvider):
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service

    async def get_context_chunks(self, query: str) -> list[str]:
        return await self.rag_service.get_context_chunks(query)