"""
Main application entry point for the MindPal platform.
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from assessment.quiz.presentation.api_router import api_router as assessment_api_router
from chat.application.exceptions.exception import (
    ConversationCreationFailureException,
    ConversationNotFoundException,
    InvalidMessageException,
)
from chat.infrastructure.database.session import init_chat_db
from chat.infrastructure.event_handler.ingestion_bridge import bridge_conversation_to_ingestion
from chat.presentation.api_router import api_router as chat_api_router
from chat.presentation.middleware.exception_handler import exception_handler
from ingestion.presentation.api_router import api_router as ingestion_api_router
from user_management.users.presentation.api_router import api_router as users_api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_chat_db()
    yield


app = FastAPI(title="MindPal Platform API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(InvalidMessageException, exception_handler)
app.add_exception_handler(ConversationNotFoundException, exception_handler)
app.add_exception_handler(ConversationCreationFailureException, exception_handler)
app.include_router(chat_api_router, prefix="/api/v1")
app.include_router(ingestion_api_router, prefix="/api/v1/ingestion")
app.include_router(assessment_api_router, prefix="/api/v1/assessment")
app.include_router(users_api_router, prefix="/api/v1/users")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bridge_conversation_to_ingestion())