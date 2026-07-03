from ingestion.domain.entities.resource_entity import Resource
from ingestion.domain.events.resource_events import CreateResourceEvent
from ingestion.domain.interfaces.resource_repo import IResourceRepository
from chat.domain.interfaces.events import IEventDispatcher
from ingestion.application.dtos.resource_dto import AddResourceDTO
from uuid import UUID
from typing import Optional
from ingestion.application.services.extract_text_from_image_locally_service import IExtractTextFromImageLocallyService
from ingestion.application.services.extract_text_from_image_with_gemini_service import IExtractTextFromImageWithGeminiService
from ingestion.application.services.extract_video_id_service import IExtractVideoIdService
from ingestion.application.services.transcribe_audio_service import ITranscribeAudioService
from ingestion.application.services.youtube_video_transcript import IYoutubeVideoTranscriptService
from ingestion.application.services.extract_text_from_pdf_service import IExtractTextFromPdfService
from ingestion.application.services.extraxt_bytes_from_url_service import IExtraxtBytesFromUrlService
from ingestion.application.services.file_handler_service import IFileHandlerService
from ingestion.application.exceptions.exceptions import UnsupportedResourceFormatException
from ingestion.domain.value_objects.type import Doc_type
from app.chat.infrastructure.config.settings import settings
class UploadResourceUseCase:
    def __init__(self, resource_repo: IResourceRepository, event_dispatcher: IEventDispatcher, extract_text_from_image_locally_service: IExtractTextFromImageLocallyService, extract_text_from_image_with_gemini_service: IExtractTextFromImageWithGeminiService, extract_video_id_service: IExtractVideoIdService, transcribe_audio_service: ITranscribeAudioService, youtube_video_transcript_service: IYoutubeVideoTranscriptService, extract_text_from_pdf_service: IExtractTextFromPdfService, file_handler_service: IFileHandlerService,extraxt_bytes_from_url_service: IExtraxtBytesFromUrlService):
        self.resource_repo = resource_repo
        self.event_dispatcher = event_dispatcher
        self.extract_text_from_image_locally_service = extract_text_from_image_locally_service
        self.extract_text_from_image_with_gemini_service = extract_text_from_image_with_gemini_service
        self.extract_video_id_service = extract_video_id_service
        self.transcribe_audio_service = transcribe_audio_service
        self.youtube_video_transcript_service = youtube_video_transcript_service
        self.extract_text_from_pdf_service = extract_text_from_pdf_service
        self.file_handler_service = file_handler_service
        self.extraxt_bytes_from_url_service = extraxt_bytes_from_url_service
    async def _validate_resource_input(self, subject_id: UUID,  title: str, doc_url: str) -> None:
        if not title or title.strip() == "":
            raise ValueError("Resource title cannot be empty.")
        if not doc_url or doc_url.strip() == "":
            raise ValueError("Resource URL cannot be empty.")
        # Check if the resource already exists for the subject
        existing_resources, _ = await self.resource_repo.get_resources_by_title(subject_id, title, limit=1, offset=0)
        if existing_resources:
            raise ValueError(f"Resource with title '{title}' already exists for subject {subject_id}.")
    async def upload_resource(self, subject_id: UUID, title: str, doc_url: str) -> AddResourceDTO:
        await self._validate_resource_input(subject_id,  title, doc_url)
        document_type = await self.file_handler_service.handle_file(doc_url)
        content: Optional[str] = None
        if document_type == Doc_type.IMAGE and settings.USE_LOCAL_LLM:
            image_bytes = await self.extraxt_bytes_from_url_service.extract_bytes_from_url(doc_url)
            content = await self.extract_text_from_image_locally_service.extract_text_from_image_locally(image_bytes)
        elif document_type == Doc_type.IMAGE and not settings.USE_LOCAL_LLM:
            image_bytes = await self.extraxt_bytes_from_url_service.extract_bytes_from_url(doc_url)
            content = await self.extract_text_from_image_with_gemini_service.extract_text_from_image_with_gemini(image_bytes)  
        elif document_type == Doc_type.VIDEO:
            video_id = await self.extract_video_id_service.extract_video_id(doc_url)
            content = await self.youtube_video_transcript_service.get_youtube_video_transcript(video_id, doc_url)
        elif document_type == Doc_type.AUDIO:
            audio_bytes = await self.extraxt_bytes_from_url_service.extract_bytes_from_url(doc_url)
            content = await self.transcribe_audio_service.transcribe_audio(audio_bytes, doc_url)
        elif document_type == Doc_type.PDF:
            pdf_bytes = await self.extraxt_bytes_from_url_service.extract_bytes_from_url(doc_url)
            content = await self.extract_text_from_pdf_service.extract_text_from_pdf(pdf_bytes)
        if content is None:
            raise UnsupportedResourceFormatException(f"Unsupported resource format for URL '{doc_url}'.")
        # Create the resource entity
        resource = Resource.create(subject_id=subject_id, doc_type=document_type, title=title, doc_url=doc_url, content=content)
        # Save the resource using the repository
        await self.resource_repo.save_resource(resource)
        # Publish the CreateResourceEvent
        event = CreateResourceEvent(
            resource_id=resource.id,
            subject_id=resource.subject_id,
            doc_type=resource.doc_type,
            title=resource.title.value,
            doc_url=resource.doc_url.value,
            content=resource.content.value
        )
        await self.event_dispatcher.dispatch(event)
        # Return a DTO representation of the resource
        return AddResourceDTO(
            id=resource.id,
            subject_id=resource.subject_id,
            doc_type=resource.doc_type,
            title=resource.title.value,
            doc_url=resource.doc_url.value,
            content=resource.content.value,
            created_at=resource.created_at
        )
    async def execute(self, subject_id: UUID, title: str, doc_url: str) -> AddResourceDTO:
        return await self.upload_resource(subject_id, title, doc_url)
        
