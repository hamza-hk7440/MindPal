from fastapi import APIRouter, Depends, status
from chat.presentation.schemas.conversation_schema import CreateConversationRequest, ConversationResponse
from chat.presentation.controllers.conversation_controller import ConversationController
from chat.presentation.dependencies import get_conversation_controller

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.post(
    "/", 
    response_model=ConversationResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat conversation session"
)
async def create_conversation(
    conversation_data: CreateConversationRequest,
    controller: ConversationController = Depends(get_conversation_controller)
) -> ConversationResponse:
    return await controller.create_conversation(conversation_data)