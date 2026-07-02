from abc import abstractmethod
from chat.domain.interfaces.base import DomainEvent
class IEventDispatcher:
    @abstractmethod
    async def dispatch(self, event: DomainEvent) -> None:
        pass