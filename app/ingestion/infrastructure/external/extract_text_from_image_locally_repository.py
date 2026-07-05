from ingestion.application.services.extract_text_from_image_locally_service import IExtractTextFromImageLocallyService
import easyocr
class ExtractTextFromImageLocallyService(IExtractTextFromImageLocallyService):
    async def extract_text_from_image_locally(self, image_bytes: bytes) -> str:
        try:
            reader = easyocr.Reader(['en','fr',])
            result = await reader.readtext(image_bytes, detail=0)
            return "".join(result)
        except Exception as e:
            raise ValueError(f"Error occurred while extracting text from image locally: {str(e)}")
        