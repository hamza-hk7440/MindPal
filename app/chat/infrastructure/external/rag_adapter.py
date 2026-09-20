import asyncio
import re

from chat.domain.interfaces.rag_provider import IRAGProvider
from ingestion.application.use_cases.queries.provide_relevant_chunks_uc import ProvideRelevantChunksUseCase
from ingestion.domain.interfaces.resource_repo import IResourceRepository

class RAGAdapter(IRAGProvider):
    def __init__(self, rag_service: ProvideRelevantChunksUseCase, resource_repo: IResourceRepository | None = None):
        self.rag_service = rag_service
        self.resource_repo = resource_repo

    async def _get_keyword_chunks(self, query: str, subject_id: str) -> list[str]:
        chunks_repo = getattr(self.rag_service, "chunks_repo", None)
        if chunks_repo is None or not hasattr(chunks_repo, "_table"):
            return []

        terms = []
        for term in re.findall(r"[A-Za-zÀ-ÿ0-9]{2,}", query.lower()):
            if term not in terms:
                terms.append(term)

        if not terms:
            return []

        chunks = []
        for term in terms[:4]:
            response = await (
                chunks_repo._table()
                .select("content")
                .eq("study_subject", str(subject_id))
                .ilike("content", f"%{term}%")
                .limit(4)
                .execute()
            )
            for row in response.data or []:
                content = row.get("content")
                if content and content not in chunks:
                    chunks.append(content)
            if len(chunks) >= 8:
                break

        return chunks[:8]

    async def _get_resource_chunks(self, subject_id: str) -> list[str]:
        if self.resource_repo is None:
            return []

        resources, _total = await self.resource_repo.get_all_resources(subject_id, limit=8, offset=0)
        chunks = []
        for resource in resources:
            title = getattr(getattr(resource, "title", ""), "value", getattr(resource, "title", ""))
            content = getattr(getattr(resource, "content", ""), "value", getattr(resource, "content", ""))
            if content:
                chunks.append(f"Document: {title}\n\n{content}")

        return chunks

    async def get_context_chunks(self, query: str, subject_id: str) -> list[str]:
        try:
            results = await asyncio.wait_for(
                self.rag_service.execute(
                    query=query,
                    threshold=0.15,
                    count=8,
                    filter_subject_id=subject_id,
                ),
                timeout=20,
            )
            chunks = [
                item.get("content", str(item)) if isinstance(item, dict) else getattr(item, "content", str(item))
                for item in results
            ]
        except Exception:
            chunks = []

        try:
            resource_chunks = await asyncio.wait_for(self._get_resource_chunks(subject_id), timeout=10)
        except Exception:
            resource_chunks = []

        for chunk in resource_chunks:
            if chunk not in chunks:
                chunks.append(chunk)

        if chunks:
            return chunks[:12]

        try:
            chunks = await asyncio.wait_for(self._get_keyword_chunks(query, subject_id), timeout=10)
        except Exception:
            chunks = []

        if chunks:
            return chunks

        return resource_chunks[:8]
