from fastapi import HTTPException
from chat.presentation.schemas.message_schema import SendMessageRequest
from chat.application.use_cases.commands.send_message_uc import SendMessageUseCase
from chat.application.use_cases.commands.generate_response_uc import GenerateResponseUseCase
from chat.application.use_cases.queries.fetch_message import FetchMessageUseCase

class MessageController:
    def __init__(self, send_message_uc: SendMessageUseCase, generate_response_uc: GenerateResponseUseCase, fetch_message_uc: FetchMessageUseCase):
        self.send_message_uc = send_message_uc
        self.generate_response_uc = generate_response_uc
        self.fetch_message_uc = fetch_message_uc

    async def stream_message_response(self, conversation_id: str, content: str, sender_role: str = "user"):
        """
        Orchestrates and yields event steps (status, token deltas) 
        live over the WebSocket protocol.
        """
        try:
            # 1. Notify client that prompt is being saved
            yield {"event": "status", "message": "Saving incoming prompt..."}
            await self.send_message_uc.execute(
                conversation_id=conversation_id,
                content=content,
                sender=sender_role
            )

            # 2. Notify client that context chunks are being evaluated
            yield {"event": "status", "message": "Thinking... analyzing knowledge base documents."}
            
            # 3. Stream text string fragments directly out of Gemini and wrap them cleanly
            async for token in self.generate_response_uc.execute_stream(conversation_id, content):
                if token:
                    yield {"event": "token_delta", "text": token}
            
            # 4. Signal clean ending
            yield {"event": "generation_finished"}

        except Exception as e:
            yield {"event": "error", "message": f"Streaming lifecycle failure: {str(e)}"}

    async def send_message(self, request: SendMessageRequest):
        try:
            return await self.send_message_uc.execute(
                conversation_id=request.conversation_id,
                content=request.content,
                sender=request.sender_role
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def generate_response(self, request: SendMessageRequest):
        try:
            response_dto = await self.generate_response_uc.generate_response(
                conversation_id=request.conversation_id,
                content=request.content
            )
            return response_dto
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def fetch_messages(self, conversation_id: str, skip: int = 0, limit: int = 100):
        try:
            return await self.fetch_message_uc.fetch_messages_by_conversation_id(conversation_id, skip, limit)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def save_request_and_get_response(self, request: SendMessageRequest):
        try:
            user_message_dto = await self.send_message_uc.execute(
                conversation_id=request.conversation_id,
                content=request.content,
                sender=request.sender_role
            )
            ai_response_dto = await self.generate_response_uc.generate_response(
                conversation_id=request.conversation_id,
                content=request.content
            )
            return {
                "user_message": user_message_dto,
                "ai_response": ai_response_dto
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))