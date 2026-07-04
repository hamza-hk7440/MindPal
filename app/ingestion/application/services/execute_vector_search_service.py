from abc import ABC, abstractmethod
from uuid import UUID

class IExecuteVectorSearchService(ABC):
    @abstractmethod
    async def execute_vector_search(self, query_vector: list[float], threshold: float,count: int,filter_subject_id: UUID) -> list[dict]:
        pass