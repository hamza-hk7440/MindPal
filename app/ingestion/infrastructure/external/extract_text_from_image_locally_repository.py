import io

from ingestion.application.services.extract_text_from_image_locally_service import IExtractTextFromImageLocallyService
import easyocr
from PIL import Image
import numpy as np
class ExtractTextFromImageLocallyService(IExtractTextFromImageLocallyService):
    def __init__(self):
        self.reader = easyocr.Reader(['en', 'fr'])  
    async def extract_text_from_image_locally(self, image_bytes: bytes) -> str:
        try:
            image=Image.open(io.BytesIO(image_bytes))
            image_np=np.array(image)
            result = self.reader.readtext(image_bytes, detail=0)
            return "".join(result)
        except Exception as e:
            raise ValueError(f"Error occurred while extracting text from image locally: {str(e)}")
        