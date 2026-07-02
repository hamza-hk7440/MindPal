from fastapi import APIRouter
from chat.presentation.routes.conversation_routes import router as conversation_router
from chat.presentation.routes.message_routes import router as message_router

api_router = APIRouter()
api_router.include_router(conversation_router)
api_router.include_router(message_router)