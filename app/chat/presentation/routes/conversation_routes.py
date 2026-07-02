from fastapi import APIRouter, Depends
from chat.presentation.schemas.conversation_schema import CreateConversationRequest, ConversationResponse
from chat.presentation.controllers.conversation_controller import ConversationController
from chat.presentation.dependencies import get_conversation_controller
router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: CreateConversationRequest,
    controller: ConversationController = Depends(get_conversation_controller)
):
    return await controller.create_conversation(conversation_data)