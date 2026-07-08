from uuid import UUID
from typing import Optional, Any
from fastapi import File
from ingestion.domain.entities.resource_entity import Resource
from ingestion.domain.events.resource_events import CreateResourceEvent
from ingestion.domain.interfaces.resource_repo import IResourceRepository
from chat.domain.interfaces.events import IEventDispatcher
from ingestion.application.dtos.resource_dto import AddResourceDTO
from ingestion.application.services.extract_bytes_from_url_service import IExtractBytesFromUrlService
from ingestion.application.services.extract_text_from_pdf_service import IExtractTextFromPdfService
from ingestion.application.services.transcribe_audio_service import ITranscribeAudioService
from ingestion.application.services.extract_video_id_service import IExtractVideoIdService
from ingestion.application.services.file_handler_service import IFileHandlerService
from ingestion.application.services.extract_text_from_image_locally_service import IExtractTextFromImageLocallyService
from ingestion.application.services.extract_text_from_image_with_gemini_service import IExtractTextFromImageWithGeminiService
from ingestion.application.services.youtube_video_transcript import IYoutubeVideoTranscriptService
from ingestion.application.exceptions.exceptions import UnsupportedResourceFormatException, IngestionValidationException
from ingestion.domain.value_objects.type import Doc_type
from chat.infrastructure.config.settings import settings

class UploadResourceUseCase:
    def __init__(
        self,
        resource_repo: IResourceRepository,
        event_dispatcher: IEventDispatcher,
        file_handler_service: IFileHandlerService,
        extract_bytes_from_url_service: IExtractBytesFromUrlService,
        extract_text_from_pdf_service: IExtractTextFromPdfService,
        transcribe_audio_service: ITranscribeAudioService,
        extract_video_id_service: IExtractVideoIdService,
        youtube_video_transcript_service: IYoutubeVideoTranscriptService,
        extract_text_from_image_locally_service: IExtractTextFromImageLocallyService,
        extract_text_from_image_with_gemini_service: IExtractTextFromImageWithGeminiService
    ):
        self.resource_repo = resource_repo
        self.event_dispatcher = event_dispatcher
        self.file_handler_service = file_handler_service
        self.extract_bytes_from_url_service = extract_bytes_from_url_service
        self.extract_text_from_pdf_service = extract_text_from_pdf_service
        self.transcribe_audio_service = transcribe_audio_service
        self.extract_video_id_service = extract_video_id_service
        self.extract_youtube_video_transcript_service = youtube_video_transcript_service
        self.extract_text_from_image_locally_service = extract_text_from_image_locally_service
        self.extract_text_from_image_with_gemini_service = extract_text_from_image_with_gemini_service

    async def execute(self, subject_id: UUID, title: str, doc_url: Optional[str], 
                      file_bytes: Optional[bytes], file: Optional[File] = None) -> AddResourceDTO:
        
        await self._validate_resource_input(subject_id, title)
        doc_type = await self._determine_doc_type(doc_url, file_bytes)
        content = await self._extract_content(doc_type, doc_url, file_bytes, file)
        
        if content is None:
            raise UnsupportedResourceFormatException("Failed to extract valid structural content.")
        
        resource_entity = Resource.create(
            subject_id=subject_id, title=title, 
            doc_url=doc_url or f"uploaded://{title}", 
            doc_type=doc_type, content=content
        )
        saved_resource = await self.resource_repo.save_resource(resource_entity)
        
        await self.event_dispatcher.dispatch(CreateResourceEvent(**saved_resource.to_dict()))
        return self._map_to_dto(saved_resource)

    async def _validate_resource_input(self, subject_id: UUID, title: str) -> None:
        if not title or title.strip() == "":
            raise IngestionValidationException("Resource title cannot be empty.")
        if await self.resource_repo.exists_by_title(subject_id, title):
            raise IngestionValidationException(f"Resource '{title}' already exists.")

    async def _determine_doc_type(self, doc_url: Optional[str], file_bytes: Optional[bytes]) -> Doc_type:
        if file_bytes:
            return await self.file_handler_service.handle_file(file_bytes)
        if doc_url:
            url_lower = doc_url.lower()
            if any(h in url_lower for h in ["youtube.com", "youtu.be"]): return Doc_type.VIDEO
            if url_lower.endswith(".pdf"): return Doc_type.PDF
        return Doc_type.TEXT

    async def _extract_content(self, doc_type: Doc_type, doc_url: Optional[str], 
                               incoming_bytes: Optional[bytes], file: Any) -> Optional[str]:
        # Route audio immediately using the file object
        if doc_type == Doc_type.AUDIO:
            return await self.transcribe_audio_service.transcribe_audio(file)

        # Route remaining types by fetching bytes first
        raw_bytes = incoming_bytes or (await self.extract_bytes_from_url_service.extract_bytes_from_url(doc_url) if doc_url else None)
        if not raw_bytes: return None

        handlers = {
            Doc_type.PDF: self.extract_text_from_pdf_service.extract_text_from_pdf,
            Doc_type.VIDEO: lambda _: self._handle_video(doc_url),
            Doc_type.IMAGE: lambda b: self._handle_image(b)
        }
        
        handler = handlers.get(doc_type)
        return await handler(raw_bytes) if handler else None

    async def _handle_video(self, doc_url: Optional[str]) -> Optional[str]:
        if not doc_url: return None
        video_id = await self.extract_video_id_service.extract_video_id(doc_url)
        return await self.extract_youtube_video_transcript_service.get_youtube_video_transcript(video_id, doc_url)

    async def _handle_image(self, raw_bytes: bytes) -> str:
        service = self.extract_text_from_image_locally_service if settings.USE_LOCAL_LLM else self.extract_text_from_image_with_gemini_service
        return await service.extract_text_from_image(raw_bytes)

    def _map_to_dto(self, resource) -> AddResourceDTO:
        def _get(attr): return attr.value if hasattr(attr, "value") else str(attr)
        return AddResourceDTO(
            id=str(resource.id), subject_id=str(resource.subject_id),
            title=_get(resource.title), doc_url=_get(resource.doc_url),
            doc_type=resource.doc_type, content=_get(resource.content),
            created_at=resource.created_at
        )