from abc import ABC, abstractmethod

class IExtractTextFromImageLocallyService(ABC):
    @abstractmethod
    async def extract_text_from_image_locally(self,file_bytes:bytes) -> str:
        pass