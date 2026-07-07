import io
import pypdf

from ingestion.application.services.extract_text_from_pdf_service import IExtractTextFromPdfService
class ExtractTextFromPdfService(IExtractTextFromPdfService):
    async def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        try:
            with io.BytesIO(file_bytes) as pdf_file:
                reader = pypdf.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()+"\n"
                return text
        except Exception as e:
            raise ValueError(f"Error occurred while extracting text from PDF: {str(e)}")
        