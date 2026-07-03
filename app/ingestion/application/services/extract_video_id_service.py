from abc import ABC, abstractmethod

class IExtractVideoIdService(ABC):
    @abstractmethod
    async def extract_video_id(self, url: str) -> str:
        pass
