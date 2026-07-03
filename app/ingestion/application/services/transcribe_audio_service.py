from abc import ABC, abstractmethod

class ITranscribeAudioService(ABC):
    @abstractmethod
    async def transcribe_audio(self, file_bytes: bytes,filename:str) -> str:
        pass