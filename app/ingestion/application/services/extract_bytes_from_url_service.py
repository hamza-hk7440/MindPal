from abc import ABC, abstractmethod

class IExtractBytesFromUrlService(ABC):
    @abstractmethod
    async def extract_bytes_from_url(self, url: str) -> bytes:
        pass