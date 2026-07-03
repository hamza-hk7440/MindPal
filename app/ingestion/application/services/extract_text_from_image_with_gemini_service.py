from abc import ABC, abstractmethod

class IExtractTextFromImageWithGeminiService(ABC):
    @abstractmethod
    async def extract_text_from_image_with_gemini(self, file_bytes: bytes) -> str:
        pass