from abc import ABC, abstractmethod

class IExtraxtBytesFromUrlService(ABC):
    @abstractmethod
    async def extract_bytes_from_url(self, url: str) -> bytes:
        pass