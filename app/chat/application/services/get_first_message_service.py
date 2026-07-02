from abc import ABC, abstractmethod
from uuid import UUID
class IGetFirstMessageService(ABC):
    @abstractmethod
    async def get_first_message(self, subject_id: UUID) -> str:
        pass
