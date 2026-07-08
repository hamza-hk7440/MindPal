import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from ingestion.application.services.youtube_video_transcript import IYoutubeVideoTranscriptService
from ingestion.application.exceptions.exceptions import IngestionExternalServiceException

class YoutubeVideoTranscriptService(IYoutubeVideoTranscriptService):
    async def get_youtube_video_transcript(self, video_id: str, url: str) -> str:
        def _fetch_transcript():
            api = YouTubeTranscriptApi()
            return api.fetch(video_id, languages=['en', 'fr'])

        try:
            transcript_data = await asyncio.to_thread(_fetch_transcript)
            # FetchedTranscript.snippets contains the transcript entries
            return " ".join([snippet.text for snippet in transcript_data.snippets])
            
        except Exception as e:
            raise IngestionExternalServiceException(f"Could not fetch transcript for {video_id}: {str(e)}")