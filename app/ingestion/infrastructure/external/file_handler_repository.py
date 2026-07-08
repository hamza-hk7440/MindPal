import filetype
from ingestion.application.exceptions.exceptions import UnsupportedResourceFormatException
from ingestion.domain.value_objects.type import Doc_type
from ingestion.application.services.file_handler_service import IFileHandlerService
class FileHandlerService(IFileHandlerService):
    async def handle_file(self, file_bytes: bytes) -> Doc_type:
        print("DEBUG: Entered FileHandlerService") # This WILL print
        
        kind = filetype.guess(file_bytes)
        mime = kind.mime if kind else "unknown"
        print(f"DEBUG: Guessed MIME: {mime}") # Crucial for debugging
        
        # Fallback check if kind is None or unidentified
        if not kind:
            print("DEBUG: filetype failed to identify. Defaulting to audio/m4a check.")
            # If the header suggests mp4/m4a (container 'ftyp')
            if file_bytes[4:12] == b'ftypM4A ' or file_bytes[4:12] == b'ftypmp42':
                return Doc_type.AUDIO

        if "pdf" in mime:
            return Doc_type.PDF
        if "image" in mime:
            return Doc_type.IMAGE
        if "audio" in mime or mime == "video/mp4": 
            return Doc_type.AUDIO
        if "video" in mime:
            return Doc_type.VIDEO

        raise UnsupportedResourceFormatException(f"Unsupported file type: {mime}")