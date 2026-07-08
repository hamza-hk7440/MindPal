from abc import ABC, abstractmethod
from fastapi import UploadFile
class ITranscribeAudioService(ABC):
    @abstractmethod
    async def transcribe_audio(self, file: UploadFile) -> str:
        pass