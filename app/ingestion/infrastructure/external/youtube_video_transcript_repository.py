from ingestion.application.services.youtube_video_transcript import IYoutubeVideoTranscriptService
from youtube_transcript_api import YouTubeTranscriptApi
class YoutubeVideoTranscriptService(IYoutubeVideoTranscriptService):
    async def get_youtube_video_transcript(self, video_id: str, url: str) -> str:
        try:
            transcript_list = YoutubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([entry["text"] for entry in transcript_list])
            return transcript_text
        except Exception as e:
            raise ValueError("Error occurred while fetching YouTube video transcript")