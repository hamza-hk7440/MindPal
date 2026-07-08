# MindPal/app/ingestion/presentation/schemas/dependencies.py

from fastapi import Depends
from supabase import AsyncClient

from ingestion.application.use_cases.commands.create_study_subject_uc import CreateStudySubjectUseCase
from ingestion.application.use_cases.commands.delete_resource_uc import DeleteResourceUseCase
from ingestion.application.use_cases.commands.delete_study_subject_uc import DeleteStudySubjectUseCase
from ingestion.application.use_cases.commands.split_resources_into_chunks_uc import SplitResourcesIntoChunksUseCase
from ingestion.application.use_cases.commands.upload_resource_uc import UploadResourceUseCase
from ingestion.application.use_cases.commands.vectorize_chunks_uc import VectorizeChunksUseCase
from ingestion.application.use_cases.queries.fetch_all_resources import FetchAllResourcesUseCase
from ingestion.application.use_cases.queries.fetch_study_subject_uc import FetchStudySubjectUseCase
from ingestion.application.use_cases.queries.provide_relevant_chunks_uc import ProvideRelevantChunksUseCase

from ingestion.infrastructure.database.repositories.chunks_repository import ChunksRepository
from ingestion.infrastructure.database.repositories.resource_repository import ResourceRepository
from ingestion.infrastructure.database.repositories.study_subject_repository import StudySubjectRepository
from ingestion.infrastructure.external.execute_vector_search_repository import ExecuteVectorSearchService
from ingestion.infrastructure.external.extract_text_from_image_locally_repository import ExtractTextFromImageLocallyService
from ingestion.infrastructure.external.extract_text_from_image_with_gemini_repository import ExtractTextFromImageWithGeminiService
from ingestion.infrastructure.external.extract_text_from_pdf_repository import ExtractTextFromPdfService
from ingestion.infrastructure.external.extract_video_id_repository import ExtractVideoIdService
from ingestion.infrastructure.external.extract_bytes_from_url_service_repository import ExtractBytesFromUrlService
from ingestion.infrastructure.external.file_handler_repository import FileHandlerService
from ingestion.infrastructure.external.slice_document_into_chunks_repository import SliceDocumentIntoChunksService
from ingestion.infrastructure.external.transcribe_audio_service_repository import TranscribeAudioService
from ingestion.infrastructure.external.vectorize_chunk_repository import VectorizeChunkService
from ingestion.infrastructure.external.youtube_video_transcript_repository import YoutubeVideoTranscriptService

from ingestion.presentation.controllers.chunks_controller import ChunksController
from ingestion.presentation.controllers.resource_controller import ResourceController
from ingestion.presentation.controllers.study_subject_controller import StudySubjectController

from chat.infrastructure.database.session import get_supabase_client
from chat.infrastructure.external.events import EventDispatcher

# --- Mock implementations for interfaces not fully provided ---
class MockEventDispatcher(EventDispatcher):
    async def dispatch(self, event):
        pass


class MockRAGProvider:
    async def get_context_chunks(self, query: str) -> list[str]:
        return []

# --- Dependency Provider Functions ---

def get_study_subject_controller(
    client: AsyncClient = Depends(get_supabase_client),
) -> StudySubjectController:
    """Provides the StudySubjectController instance."""
    study_subject_repo = StudySubjectRepository(client=client)
    event_dispatcher = MockEventDispatcher()

    create_study_subject_uc = CreateStudySubjectUseCase(
        study_subject_repo=study_subject_repo,
        event_dispatcher=event_dispatcher,
    )
    delete_study_subject_uc = DeleteStudySubjectUseCase(
        study_subject_repo=study_subject_repo,
        event_dispatcher=event_dispatcher,
    )
    fetch_study_subject_uc = FetchStudySubjectUseCase(
        study_subject_repo=study_subject_repo,
        event_dispatcher=event_dispatcher,
    )
    return StudySubjectController(
        create_study_subject_uc=create_study_subject_uc,
        delete_study_subject_uc=delete_study_subject_uc,
        fetch_study_subject_uc=fetch_study_subject_uc,
    )

def get_resource_controller(
    client: AsyncClient = Depends(get_supabase_client),
) -> ResourceController:
    """Provides the ResourceController instance."""
    resource_repo = ResourceRepository(client=client)
    study_subject_repo = StudySubjectRepository(client=client)
    event_dispatcher = MockEventDispatcher()

    extract_text_from_image_locally_service = ExtractTextFromImageLocallyService()
    extract_text_from_image_with_gemini_service = ExtractTextFromImageWithGeminiService()
    extract_text_from_pdf_service = ExtractTextFromPdfService()
    extract_video_id_service = ExtractVideoIdService()
    extract_bytes_from_url_service = ExtractBytesFromUrlService()
    file_handler_service = FileHandlerService()
    transcribe_audio_service = TranscribeAudioService()
    youtube_video_transcript_service = YoutubeVideoTranscriptService()

    upload_resource_uc = UploadResourceUseCase(
        resource_repo=resource_repo,
        event_dispatcher=event_dispatcher,
        file_handler_service=file_handler_service,
        extract_text_from_image_locally_service=extract_text_from_image_locally_service,
        extract_text_from_image_with_gemini_service=extract_text_from_image_with_gemini_service,
        extract_text_from_pdf_service=extract_text_from_pdf_service,
        transcribe_audio_service=transcribe_audio_service,
        youtube_video_transcript_service=youtube_video_transcript_service,
        extract_video_id_service=extract_video_id_service,
        extract_bytes_from_url_service=extract_bytes_from_url_service,
    )
    delete_resource_uc = DeleteResourceUseCase(
        resource_repo=resource_repo,
        study_subject_repo=study_subject_repo,
        event_dispatcher=event_dispatcher,
    )
    fetch_all_resources_uc = FetchAllResourcesUseCase(
        resource_repo=resource_repo,
        study_subject_repo=study_subject_repo,
        event_dispatcher=event_dispatcher,
    )
    return ResourceController(
        upload_resource_uc=upload_resource_uc,
        delete_resource_uc=delete_resource_uc,
        fetch_all_resources_uc=fetch_all_resources_uc,
    )

# New Cross-Module Dependency Provider
def get_provide_relevant_chunks_use_case(
    client: AsyncClient = Depends(get_supabase_client)
) -> ProvideRelevantChunksUseCase:
    """
    Exposes the RAG retrieval engine standalone.
    This allows the Chat/Message module to call vector lookups inside its WebSockets router.
    """
    chunks_repo = ChunksRepository(client=client)
    event_dispatcher = MockEventDispatcher()
    execute_vector_search_service = ExecuteVectorSearchService()
    vectorize_chunk_service = VectorizeChunkService()

    return ProvideRelevantChunksUseCase(
        chunks_repo=chunks_repo,
        event_dispatcher=event_dispatcher,
        execute_vector_search_service=execute_vector_search_service,
        vectorize_chunk_service=vectorize_chunk_service,
    )

def get_chunks_controller(
    client: AsyncClient = Depends(get_supabase_client),
    provide_relevant_chunks_uc: ProvideRelevantChunksUseCase = Depends(get_provide_relevant_chunks_use_case)
) -> ChunksController:
    """Provides the ChunksController instance using the shared query use case hook."""
    chunks_repo = ChunksRepository(client=client)
    resource_repo = ResourceRepository(client=client)
    study_subject_repo = StudySubjectRepository(client=client)
    event_dispatcher = MockEventDispatcher()

    slice_document_service = SliceDocumentIntoChunksService()
    vectorize_chunk_service = VectorizeChunkService()

    split_resources_into_chunks_uc = SplitResourcesIntoChunksUseCase(
        resource_repo=resource_repo,
        chunks_repo=chunks_repo,
        event_dispatcher=event_dispatcher,
        slice_document_service=slice_document_service,
        study_subject_repo=study_subject_repo,
    )
    vectorize_chunks_uc = VectorizeChunksUseCase(
        chunks_repo=chunks_repo,
        event_dispatcher=event_dispatcher,
        vectorize_chunk_service=vectorize_chunk_service,
    )
    
    return ChunksController(
        split_resources_into_chunks_uc=split_resources_into_chunks_uc,
        vectorize_chunks_uc=vectorize_chunks_uc,
        provide_relevant_chunks_uc=provide_relevant_chunks_uc,
    )