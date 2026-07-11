import redis
from app.core.celery_app import celery_app
from ingestion.application.use_cases.commands.upload_resource_uc import UploadResourceUseCase
from ingestion.infrastructure.external.file_handler_repository import FileHandlerService
from ingestion.infrastructure.external.extract_text_from_image_locally_repository import ExtractTextFromImageLocallyService
from ingestion.infrastructure.external.extract_text_from_image_with_gemini_repository import ExtractTextFromImageWithGeminiService
from ingestion.infrastructure.external.extract_bytes_from_url_service_repository import ExtractBytesFromUrlService
from ingestion.infrastructure.external.extract_text_from_pdf_repository import ExtractTextFromPdfService
from ingestion.infrastructure.external.transcribe_audio_service_repository import TranscribeAudioService
from ingestion.infrastructure.external.extract_video_id_repository  import ExtractVideoIdService
from ingestion.infrastructure.external.youtube_video_transcript_repository import YoutubeVideoTranscriptService

r=redis.Redis(host="localhost", port=6379, db=0)

def get_upload_resource_use_case() -> UploadResourceUseCase:
    resource_repo = r.get("resource_repo")
    event_dispatcher = r.get("event_dispatcher")
    file_handler_service = r.get("file_handler_service")
    extract_bytes_from_url_service = r.get("extract_bytes_from_url_service")
    extract_text_from_pdf_service = r.get("extract_text_from_pdf_service")
    transcribe_audio_service = r.get("transcribe_audio_service")
    extract_video_id_service = r.get("extract_video_id_service")
    youtube_video_transcript_service = r.get("youtube_video_transcript_service")
    extract_text_from_image_locally_service = r.get("extract_text_from_image_locally_service")
    extract_text_from_image_with_gemini_service = r.get("extract_text_from_image_with_gemini_service")

    return UploadResourceUseCase(
        resource_repo=resource_repo,
        event_dispatcher=event_dispatcher,
        file_handler_service=file_handler_service,
        extract_bytes_from_url_service=extract_bytes_from_url_service,
        extract_text_from_pdf_service=extract_text_from_pdf_service,
        transcribe_audio_service=transcribe_audio_service,
        extract_video_id_service=extract_video_id_service,
        youtube_video_transcript_service=youtube_video_transcript_service,
        extract_text_from_image_locally_service=extract_text_from_image_locally_service,
        extract_text_from_image_with_gemini_service=extract_text_from_image_with_gemini_service
    )

@celery_app.task(name="upload_resource_task", bind=True)
def ingest_resource_task(self, subject_id: str, title: str, doc_url: str = None, file_bytes: bytes = None, file_name: str = None):
    task_id = self.request.id
    r.set(f"task:{task_id}:progress", "25")
    try:
        upload_resource_uc = get_upload_resource_use_case()
        resource_dto = upload_resource_uc.execute(
            subject_id=subject_id,
            title=title,
            doc_url=doc_url,
            file_bytes=file_bytes,
            file_name=file_name
        )
        r.set(f"task:{task_id}:progress", "100")
        return resource_dto.model_dump()
    except Exception as e:
        r.set(f"task:{task_id}:progress", "0")
        r.set(f"task:{task_id}:error", str(e))
        raise e