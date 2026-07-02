from abc import ABC, abstractmethod
from typing import Generic, TypeVar
#generic type variable for the repository
T = TypeVar("T")

class IRepository(Generic[T], ABC):
    @abstractmethod
    async def add(self, entity: T) -> None:
        pass

    @abstractmethod
    async def get(self, entity_id: str) -> T:
        pass

    @abstractmethod
    async  def update(self, entity: T) -> None:
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> None:
        pass
class DomainEvent:
    pass
    
