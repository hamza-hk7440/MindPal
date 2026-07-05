from ingestion.application.services.extract_video_id_service import IExtractVideoIdService
import httpx
from ingestion.application.exceptions.exceptions import IngestionExternalServiceException
class ExtractVideoIdService(IExtractVideoIdService):
    async def extract_video_id(self, url: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except httpx.RequestError as e:
            raise IngestionExternalServiceException(f"Error occurred while extracting video ID: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise IngestionExternalServiceException(f"Error occurred while extracting video ID: {str(e)}") 