from groq import Groq, GroqError
from fastapi import status, HTTPException

from ingestion.application.services.transcribe_audio_service import ITranscribeAudioService
from chat.infrastructure.config.settings import settings

class TranscribeAudioService(ITranscribeAudioService):
    def __init__(self):
        self._client = Groq(api_key=settings.GROQ_API_KEY)
        self._model = "whisper-large-v3"  

    async def transcribe_audio(self, file_bytes: bytes, filename: str) -> str:
        """
        Transcribes memory-buffered file bytes into text using Groq's high-speed Whisper hardware.
        """
        try:
            # Groq's underlying HTTP layer requires a tuple containing (filename, bytes_payload)
            file_tuple = (filename, file_bytes)
            
            # Execute the Speech-to-Text inference 
            response = self._client.audio.transcriptions.create(
                file=file_tuple,
                model=self._model,
                response_format="json",
                temperature=0.0
            )
            
            # Extract and return the transcribed text string
            return response.text

        except GroqError as exc:
            # Log exact downstream error data without crashing the thread pool
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq Whisper inference failed: {str(exc)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unhandled pipeline error during text transcription: {str(e)}"
            )