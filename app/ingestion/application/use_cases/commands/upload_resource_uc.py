from uuid import UUID
from typing import Optional, Any

from fastapi import  File
from ingestion.domain.entities.resource_entity import Resource
from ingestion.domain.events.resource_events import CreateResourceEvent
from ingestion.domain.interfaces.resource_repo import IResourceRepository
from chat.domain.interfaces.events import IEventDispatcher
from ingestion.application.dtos.resource_dto import AddResourceDTO
from ingestion.application.services.extract_bytes_from_url_service import IExtractBytesFromUrlService
from ingestion.application.services.extract_text_from_pdf_service import IExtractTextFromPdfService
from ingestion.application.services.transcribe_audio_service  import ITranscribeAudioService
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

    async def _validate_resource_input(self, subject_id: UUID, title: str) -> None:
        if not title or title.strip() == "":
            raise IngestionValidationException("Resource title cannot be empty.")
            
        if await self.resource_repo.exists_by_title(subject_id, title):
            raise IngestionValidationException(f"Resource with title '{title}' already exists for subject {subject_id}.")

    async def _extract_content(self, document_type: Doc_type, doc_url: Optional[str], incoming_bytes: Optional[bytes],file:File) -> Optional[str]:
        if incoming_bytes is not None:
            raw_bytes = incoming_bytes
        elif doc_url:
            raw_bytes = await self.extract_bytes_from_url_service.extract_bytes_from_url(doc_url)
        else:
            return None

        if document_type == Doc_type.PDF:
            return await self.extract_text_from_pdf_service.extract_text_from_pdf(raw_bytes)

        if document_type == Doc_type.AUDIO:
            if incoming_bytes is None:
                print("DEBUG: Incoming bytes is None for Audio!")
            return await self.transcribe_audio_service.transcribe_audio(file)

        if document_type == Doc_type.VIDEO:
            if not doc_url:
                return None
            video_id = await self.extract_video_id_service.extract_video_id(doc_url)
            return await self.extract_youtube_video_transcript_service.get_youtube_video_transcript(video_id, doc_url)

        if document_type == Doc_type.IMAGE:
            if settings.USE_LOCAL_LLM:
                return await self.extract_text_from_image_locally_service.extract_text_from_image_locally(raw_bytes)
            return await self.extract_text_from_image_with_gemini_service.extract_text_from_image_with_gemini(raw_bytes)

        return None

    async def execute(
        self,
        subject_id: UUID,
        title: str,
        doc_url: Optional[str],
        file_bytes: Optional[bytes],
        inbound_doc_type: Optional[str] = None,
        file:Optional[File] = None
    ) -> AddResourceDTO:
        await self._validate_resource_input(subject_id, title)
        
        if file_bytes:
            bounded_doc_type = await self.file_handler_service.handle_file(file_bytes)
        elif doc_url:
            cleaned_url = doc_url.lower()
            if "youtube.com" in cleaned_url or "youtu.be" in cleaned_url:
                bounded_doc_type = Doc_type.VIDEO
            elif cleaned_url.endswith(".pdf"):
                bounded_doc_type = Doc_type.PDF
            else:
                bounded_doc_type = Doc_type.TEXT
        else:
            bounded_doc_type = Doc_type.TEXT

        content = await self._extract_content(bounded_doc_type, doc_url, file_bytes,file)

        if content is None:
            raise UnsupportedResourceFormatException("Failed to extract valid structural content from resource asset.")

        resource_entity = Resource.create(
            subject_id=subject_id,
            title=title,
            doc_url=doc_url or f"uploaded://{title}",
            doc_type=bounded_doc_type,
            content=content
        )

        saved_resource = await self.resource_repo.save_resource(resource_entity)

        create_event = CreateResourceEvent(
            resource_id=saved_resource.id,
            subject_id=saved_resource.subject_id,
            title=saved_resource.title,
            doc_url=saved_resource.doc_url,
            doc_type=saved_resource.doc_type,
            content=saved_resource.content
        )
        await self.event_dispatcher.dispatch(create_event)

        return AddResourceDTO(
            id=str(saved_resource.id),
            subject_id=str(saved_resource.subject_id),
            # Access the .value property to convert the Value Object to a primitive string
            title=saved_resource.title.value if hasattr(saved_resource.title, "value") else str(saved_resource.title),
            doc_url=saved_resource.doc_url.value if hasattr(saved_resource.doc_url, "value") else str(saved_resource.doc_url),
            doc_type=saved_resource.doc_type,
            content=saved_resource.content.value if hasattr(saved_resource.content, "value") else str(saved_resource.content),
            created_at=saved_resource.created_at
        )