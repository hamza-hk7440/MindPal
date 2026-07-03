from abc import ABC, abstractmethod

class IExtractTextFromPdfService(ABC):
    @abstractmethod
    async def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        pass