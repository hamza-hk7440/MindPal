import re
from ingestion.application.services.extract_video_id_service import IExtractVideoIdService
from ingestion.application.exceptions.exceptions import IngestionExternalServiceException

class ExtractVideoIdService(IExtractVideoIdService):
    async def extract_video_id(self, url: str) -> str:
        patterns = [
            r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/))([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise IngestionExternalServiceException(f"Could not extract a valid YouTube video ID from: {url}")