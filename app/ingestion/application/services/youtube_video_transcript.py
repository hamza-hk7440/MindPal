from abc import ABC, abstractmethod

class IYoutubeVideoTranscriptService(ABC):
    @abstractmethod
    async def get_youtube_video_transcript(self, video_id: str, url: str) -> str:
        pass