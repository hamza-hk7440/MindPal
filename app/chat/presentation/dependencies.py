from fastapi import Depends
from supabase import AsyncClient

from chat.application.use_cases.commands.create_conversation import CreateConversationUseCase
from chat.application.use_cases.commands.generate_response_uc import GenerateResponseUseCase
from chat.application.use_cases.commands.send_message_uc import SendMessageUseCase
from chat.application.use_cases.queries.fetch_message import FetchMessageUseCase
from chat.infrastructure.database.repositories.conversation_repository import ConversationRepository
from chat.infrastructure.database.repositories.message_repository import MessageRepository
from chat.infrastructure.database.session import get_supabase_client
from chat.infrastructure.external.events import EventDispatcher
from chat.infrastructure.external.gemini_client import GeminiClient
from chat.infrastructure.external.llama2_client import Llama2Client
from chat.infrastructure.external.rag_adapter import RAGAdapter
from chat.presentation.controllers.conversation_controller import ConversationController
from chat.presentation.controllers.message_controller import MessageController
from ingestion.application.use_cases.queries.provide_relevant_chunks_uc import ProvideRelevantChunksUseCase
from ingestion.infrastructure.database.repositories.chunks_repository import ChunksRepository
from ingestion.infrastructure.database.repositories.resource_repository import ResourceRepository
from ingestion.infrastructure.database.repositories.study_subject_repository import StudySubjectRepository
from ingestion.infrastructure.external.execute_vector_search_repository import ExecuteVectorSearchService
from ingestion.infrastructure.external.vectorize_chunk_repository import VectorizeChunkService

def get_message_controller(
    client: AsyncClient = Depends(get_supabase_client),
) -> MessageController:
    message_repo = MessageRepository(client=client)
    conversation_repo = ConversationRepository(client=client)
    event_dispatcher = EventDispatcher()
    gemini_service = GeminiClient()
    llama2_service = Llama2Client()
    chunks_repo = ChunksRepository(client=client)
    resource_repo = ResourceRepository(client=client)
    provide_relevant_chunks_uc = ProvideRelevantChunksUseCase(
        chunks_repo=chunks_repo,
        event_dispatcher=event_dispatcher,
        execute_vector_search_service=ExecuteVectorSearchService(),
        vectorize_chunk_service=VectorizeChunkService(),
    )
    rag_provider = RAGAdapter(provide_relevant_chunks_uc, resource_repo)

    send_message_uc = SendMessageUseCase(
        message_repo=message_repo,
        message_service=gemini_service,
        conversation_repo=conversation_repo,
        event_dispatcher=event_dispatcher,
    )
    generate_response_uc = GenerateResponseUseCase(
        message_repo=message_repo,
        gemini_service=gemini_service,
        llama2_service=llama2_service,
        conversation_repo=conversation_repo,
        event_dispatcher=event_dispatcher,
        rag_provider=rag_provider,
    )
    fetch_message_uc = FetchMessageUseCase(
        message_repo=message_repo,
        event_dispatcher=event_dispatcher,
        conversation_repo=conversation_repo,
    )
    return MessageController(send_message_uc, generate_response_uc, fetch_message_uc)


def get_conversation_controller(
    client: AsyncClient = Depends(get_supabase_client),
) -> ConversationController:
    conversation_repo = ConversationRepository(client=client)
    study_subject_repo = StudySubjectRepository(client=client)
    event_dispatcher = EventDispatcher()
    create_conversation_uc = CreateConversationUseCase(conversation_repo, event_dispatcher, study_subject_repo)
    return ConversationController(create_conversation_uc)
