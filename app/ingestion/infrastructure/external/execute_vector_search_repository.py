from ingestion.application.services.execute_vector_search_service import IExecuteVectorSearchService
from app.chat.infrastructure.database.session import get_supabase_client
from uuid import UUID
class ExecuteVectorSearchService(IExecuteVectorSearchService):
    async def execute_vector_search(self, query_vector: list[float], threshold: float,count: int,filter_subject_id: UUID):
        supabase_client = get_supabase_client()
        response = supabase_client.rpc(
            "execute_vector_search",
            {
                "query_vector": query_vector,
                "threshold": threshold,
                "count": count,
                "filter_subject_id": str(filter_subject_id)
            }
        ).execute()
        if response.status_code != 200:
            raise Exception(f"Error executing vector search: {response.status_code} - {response.text}")
        return response.data