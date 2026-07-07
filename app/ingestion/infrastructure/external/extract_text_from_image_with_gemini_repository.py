
from google.genai import types
from ingestion.application.services.extract_text_from_image_with_gemini_service import IExtractTextFromImageWithGeminiService
from chat.infrastructure.config.settings import settings
import google.generativeai as genai
class ExtractTextFromImageWithGeminiService(IExtractTextFromImageWithGeminiService):
    async def extract_text_from_image(self, image_bytes: bytes) -> str:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        try:
            response = await client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    {"data": image_bytes},
                    "Extract the text from this image. Maintain paragraphs cleanly."
                ]
            )
            return response.text
        except Exception as e:
            raise ValueError("Error occurred while extracting text from image")