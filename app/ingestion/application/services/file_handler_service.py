from abc import ABC, abstractmethod

class IFileHandlerService(ABC):
    @abstractmethod
    async def handle_file(self, file)-> str:
        pass