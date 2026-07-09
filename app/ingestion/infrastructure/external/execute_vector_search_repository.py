import asyncio
from chat.infrastructure.database.session import init_chat_db
from ingestion.application.services.execute_vector_search_service import IExecuteVectorSearchService
class ExecuteVectorSearchService(IExecuteVectorSearchService):
    async def execute_vector_search(self, query_vector, threshold, count, filter_subject_id):
        supabase_client = await init_chat_db()
        response = await supabase_client.rpc(
            "execute_vector_search",
            {
                "query_vector": query_vector,
                "threshold": threshold,
                "count": count,
                "filter_subject_id": str(filter_subject_id)
            }
        ).execute()
        
        return response.data