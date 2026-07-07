"""
Main entry point for user_management system.
"""


from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat.presentation.api_router import api_router
from ingestion.presentation.api_router import api_router as ingestion_api_router
from chat.application.exceptions.exception import (
    InvalidMessageException, 
    ConversationNotFoundException, 
    ConversationCreationFailureException
)
from chat.presentation.middleware.exception_handler import exception_handler
from chat.infrastructure.database.session import init_chat_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_chat_db()
    yield


app=FastAPI(title="MindPal Chat API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins during local development/testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(InvalidMessageException, exception_handler)
app.add_exception_handler(ConversationNotFoundException, exception_handler)
app.add_exception_handler(ConversationCreationFailureException, exception_handler)
app.include_router(api_router, prefix="/api/v1")
app.include_router(ingestion_api_router, prefix="/api/v1/ingestion")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
