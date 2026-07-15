import redis
import base64
import asyncio
from core.celery_app import celery_app

from chat.infrastructure.database.session import _get_or_create_supabase_client
from ingestion.application.use_cases.commands.upload_resource_uc import UploadResourceUseCase
from ingestion.infrastructure.external.file_handler_repository import FileHandlerService
from ingestion.infrastructure.database.repositories.resource_repository import ResourceRepository
from ingestion.infrastructure.external.extract_text_from_image_locally_repository import ExtractTextFromImageLocallyService
from ingestion.infrastructure.external.extract_text_from_image_with_gemini_repository import ExtractTextFromImageWithGeminiService
from ingestion.infrastructure.external.extract_bytes_from_url_service_repository import ExtractBytesFromUrlService
from ingestion.infrastructure.external.extract_text_from_pdf_repository import ExtractTextFromPdfService
from ingestion.infrastructure.external.transcribe_audio_service_repository import TranscribeAudioService
from ingestion.infrastructure.external.extract_video_id_repository import ExtractVideoIdService
from chat.domain.interfaces.events import IEventDispatcher
from ingestion.infrastructure.external.youtube_video_transcript_repository import YoutubeVideoTranscriptService

r = redis.Redis(host="localhost", port=6379, db=0)

async def _run_async_ingestion(subject_id, title, doc_url, incoming_bytes):
    supabase_async_client = await _get_or_create_supabase_client()
    
    uc = UploadResourceUseCase(
        file_handler_service=FileHandlerService(),
        event_dispatcher=IEventDispatcher(),
        resource_repo=ResourceRepository(client=supabase_async_client),
        extract_text_from_image_locally_service=ExtractTextFromImageLocallyService(),
        extract_text_from_image_with_gemini_service=ExtractTextFromImageWithGeminiService(),
        extract_bytes_from_url_service=ExtractBytesFromUrlService(),
        extract_text_from_pdf_service=ExtractTextFromPdfService(),
        transcribe_audio_service=TranscribeAudioService(),
        extract_video_id_service=ExtractVideoIdService(),
        youtube_video_transcript_service=YoutubeVideoTranscriptService()
    )
    
    return await uc.execute(
        subject_id=subject_id, 
        title=title, 
        doc_url=doc_url, 
        file_bytes=incoming_bytes
    )

@celery_app.task(name="ingest_resource_task", bind=True)
def ingest_resource_task(self, subject_id, title, doc_url, file_bytes):
    task_id = self.request.id
    try:
        incoming_bytes = base64.b64decode(file_bytes.encode('utf-8')) if file_bytes else None
        asyncio.run(_run_async_ingestion(subject_id, title, doc_url, incoming_bytes))        
        r.set(f"task:{task_id}:progress", "100")
        return {"status": "success"}
    except Exception as exc:
        r.set(f"task:{task_id}:error", str(exc))
        raise exc