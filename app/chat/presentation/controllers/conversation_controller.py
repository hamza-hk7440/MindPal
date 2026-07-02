from fastapi import HTTPException
from chat.presentation.schemas.conversation_schema import CreateConversationRequest, ConversationResponse
from chat.application.use_cases.commands.create_conversation import CreateConversationUseCase

class ConversationController:
    def __init__(self,create_conversation_uc: CreateConversationUseCase):
        self.create_conversation_uc = create_conversation_uc
    async def create_conversation(self, request: CreateConversationRequest) -> ConversationResponse:
        try:
            conversation_dto=await self.create_conversation_uc.create_conversation(subject_id=request.subject_id)
            return ConversationResponse.model_validate(conversation_dto)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        

