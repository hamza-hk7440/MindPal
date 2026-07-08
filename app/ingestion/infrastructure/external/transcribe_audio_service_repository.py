import io
from groq import Groq
from fastapi import UploadFile
from ingestion.application.services.transcribe_audio_service import ITranscribeAudioService
from chat.infrastructure.config.settings import settings

class TranscribeAudioService(ITranscribeAudioService):
    def __init__(self):
        self._client = Groq(api_key=settings.GROQ_API_KEY)
        self._model = "whisper-large-v3"

    async def transcribe_audio(self, file: UploadFile) -> str:
    # Ensure the file pointer is at the start
        await file.seek(0) 
        
        try:
            # Groq/OpenAI SDKs love receiving the file object directly
            response = self._client.audio.transcriptions.create(
                file=(file.filename, file.file), # file.file is the underlying spooled file object
                model=self._model,
                response_format="json",
                temperature=0.0
            )
            return response.text
        except Exception as e:
            print(f"DEBUG: Error: {e}")
            raise