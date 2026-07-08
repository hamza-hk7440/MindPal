from ingestion.application.services.extract_bytes_from_url_service import IExtractBytesFromUrlService
class ExtractBytesFromUrlService(IExtractBytesFromUrlService):
    async def extract_bytes_from_url(self, url: str) -> bytes:
        import requests
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise ValueError("Error occurred while extracting bytes from URL")