from uuid import UUID
from typing import Optional, Any

from ingestion.domain.entities.resource_entity import Resource
from ingestion.domain.events.resource_events import CreateResourceEvent
from ingestion.domain.interfaces.resource_repo import IResourceRepository
from chat.domain.interfaces.events import IEventDispatcher
from ingestion.application.dtos.resource_dto import AddResourceDTO
from ingestion.application.services.extraxt_bytes_from_url_service import IExtraxtBytesFromUrlService
from ingestion.application.services.file_handler_service import IFileHandlerService
from ingestion.application.exceptions.exceptions import UnsupportedResourceFormatException, IngestionValidationException
from ingestion.domain.value_objects.type import Doc_type
from app.chat.infrastructure.config.settings import settings


class UploadResourceUseCase:
    def __init__(
        self,
        resource_repo: IResourceRepository,
        event_dispatcher: IEventDispatcher,
        file_handler_service: IFileHandlerService,
        extraxt_bytes_from_url_service: IExtraxtBytesFromUrlService,
        **extractor_services: Any
    ):
        self.resource_repo = resource_repo
        self.event_dispatcher = event_dispatcher
        self.file_handler_service = file_handler_service
        self.extraxt_bytes_from_url_service = extraxt_bytes_from_url_service
        
        # Unpack specialized text extraction dependencies safely
        self._extractors = extractor_services

    async def _validate_resource_input(self, subject_id: UUID, title: str) -> None:
        if not title or title.strip() == "":
            raise IngestionValidationException("Resource title cannot be empty.")
            
        # Use our optimized optimized check method
        if await self.resource_repo.exists_by_title(subject_id, title):
            raise IngestionValidationException(f"Resource with title '{title}' already exists for subject {subject_id}.")

    async def _extract_content(self, document_type: Doc_type, doc_url: str) -> Optional[str]:
        """Dispatches extraction to the appropriate service strategy, reducing complexity."""
        if document_type == Doc_type.PDF:
            pdf_bytes = await self.extraxt_bytes_from_url_service.extract_bytes_from_url(doc_url)
            return await self._extractors["extract_text_from_pdf_service"].extract_text_from_pdf(pdf_bytes)

        if document_type == Doc_type.AUDIO:
            audio_bytes = await self.extraxt_bytes_from_url_service.extract_bytes_from_url(doc_url)
            return await self._extractors["transcribe_audio_service"].transcribe_audio(audio_bytes, doc_url)

        if document_type == Doc_type.VIDEO:
            video_id = await self._extractors["extract_video_id_service"].extract_video_id(doc_url)
            return await self._extractors["youtube_video_transcript_service"].get_youtube_video_transcript(video_id, doc_url)

        if document_type == Doc_type.IMAGE:
            image_bytes = await self.extraxt_bytes_from_url_service.extract_bytes_from_url(doc_url)
            if settings.USE_LOCAL_LLM:
                return await self._extractors["extract_text_from_image_locally_service"].extract_text_from_image_locally(image_bytes)
            return await self._extractors["extract_text_from_image_with_gemini_service"].extract_text_from_image_with_gemini(image_bytes)

        return None

    async def execute(self, subject_id: UUID, title: str, doc_url: str) -> AddResourceDTO:
        if not doc_url or doc_url.strip() == "":
            raise IngestionValidationException("Resource URL cannot be empty.")
            
        await self._validate_resource_input(subject_id, title)
        
        document_type = await self.file_handler_service.handle_file(doc_url)
        content = await self._extract_content(document_type, doc_url)
        
        if content is None:
            raise UnsupportedResourceFormatException(f"Unsupported resource format for URL '{doc_url}'.")

        resource = Resource.create(
            subject_id=subject_id, 
            doc_type=document_type, 
            title=title, 
            doc_url=doc_url, 
            content=content
        )
        
        await self.resource_repo.save_resource(resource)

        await self.event_dispatcher.dispatch(
            CreateResourceEvent(
                resource_id=resource.id,
                subject_id=resource.subject_id,
                doc_type=resource.doc_type,
                title=resource.title.value,
                doc_url=resource.doc_url.value,
                content=resource.content.value
            )
        )

        return AddResourceDTO(
            id=resource.id,
            subject_id=resource.subject_id,
            doc_type=resource.doc_type,
            title=resource.title.value,
            doc_url=resource.doc_url.value,
            content=resource.content.value,
            created_at=resource.created_at
        )