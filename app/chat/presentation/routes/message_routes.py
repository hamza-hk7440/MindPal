from uuid import UUID
from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect
from typing import List
import json

from chat.presentation.schemas.message_schema import SendMessageRequest, MessageResponse
from chat.presentation.controllers.message_controller import MessageController
from chat.presentation.dependencies import get_message_controller

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.websocket("/ws/{conversation_id}")
async def message_stream_ws(
    conversation_id: UUID, 
    websocket: WebSocket, 
    controller: MessageController = Depends(get_message_controller)
):
    """
    Live WebSocket endpoint that unifies 'save-request-and-get-response'.
    Receives user prompts, invokes context retrieval, and streams back real-time tokens.
    """
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            payload = json.loads(raw_data)
            user_content = payload.get("content")
            
            if not user_content:
                await websocket.send_json({"event": "error", "message": "Message content is missing."})
                continue

            async for token in controller.stream_message_response(conversation_id, user_content):
                await websocket.send_json(token)

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({"event": "error", "message": str(exc)})
        except Exception:
            pass


@router.post(
    "/", 
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Manually log or save a standalone message"
)
async def send_message(
    request: SendMessageRequest, 
    controller: MessageController = Depends(get_message_controller)
) -> MessageResponse:
    return await controller.send_message(request)


@router.get(
    "/{conversation_id}",
    response_model=List[MessageResponse],
    summary="Fetch paginated historic chat messages matching a conversation context"
)
async def fetch_messages(
    conversation_id: UUID,  
    skip: int = 0, 
    limit: int = 100, 
    controller: MessageController = Depends(get_message_controller)
) -> List[MessageResponse]:
    return await controller.fetch_messages(conversation_id, skip, limit)