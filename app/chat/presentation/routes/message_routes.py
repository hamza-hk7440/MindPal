from fastapi import APIRouter, Depends
from chat.presentation.schemas.message_schema import SendMessageRequest, MessageResponse
from chat.presentation.controllers.message_controller import MessageController
from chat.presentation.dependencies import get_message_controller
router = APIRouter(prefix="/messages", tags=["Messages"])

@router.post("/", response_model=MessageResponse)
async def send_message(request: SendMessageRequest, controller: MessageController = Depends(get_message_controller)):
    return await controller.send_message(request)

@router.post("/generate-response", response_model=MessageResponse)
async def generate_response(request: SendMessageRequest, controller: MessageController = Depends(get_message_controller)):
    return await controller.generate_response(request)
@router.get("/{conversation_id}")
async def fetch_messages(conversation_id: str, skip: int = 0, limit: int = 100, controller: MessageController = Depends(get_message_controller)):
    return await controller.fetch_messages(conversation_id, skip, limit)

@router.post("/save-request-and-get-response", response_model=dict)
async def save_request_and_get_response(request: SendMessageRequest, controller: MessageController = Depends(get_message_controller)):
    return await controller.save_request_and_get_response(request)
