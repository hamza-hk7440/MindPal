from ingestion.application.services.transcribe_audio_service import ITranscribeAudioService
from app.chat.infrastructure.config.settings import settings
from xai_sdk import Client as XAIClient
grok_client = XAIClient(api_key=settings.XAI_API_KEY)
class TranscribeAudioService(ITranscribeAudioService):
    async def transcribe_audio(self, file_bytes: bytes, filename: str) -> str:
        try :
            file_tuple = (filename, file_bytes)
            response=grok_client.audio.transcriptions.create(
                file=file_tuple,
                model="whisper-large-v3",
                response_format="json",
                temperature=0.0
            )
            return response.text if hasattr(response, 'text') else str(response)
        except Exception as e:
            raise ValueError("Error occurred while transcribing audio")
        
