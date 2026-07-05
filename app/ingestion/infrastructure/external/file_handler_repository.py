from ingestion.application.services.file_handler_service import IFileHandlerService
import filetype
from ingestion.application.exceptions.exceptions import UnsupportedResourceFormatException
from ingestion.domain.value_objects.type import Doc_type
class FileHandlerService(IFileHandlerService):
    async def handle_file(self, file) -> str:
        try:
            # Read the file bytes
            file_bytes = await file.read()

            # Determine the file type
            kind = filetype.guess(file_bytes)
            if kind is None:
                raise UnsupportedResourceFormatException("Cannot determine the file type.")
            mime=kind.mime
            # Handle based on the file type
            if "pdf" in mime:
                return Doc_type.PDF
            if "image" in mime:
                return Doc_type.IMAGE
            if "audio" in mime:
                return Doc_type.AUDIO
            if "video" in mime:
                return Doc_type.VIDEO
            raise UnsupportedResourceFormatException(f"Unsupported file type: {kind.mime}")
        except Exception as e:
            raise UnsupportedResourceFormatException(f"Error occurred while handling the file: {str(e)}")