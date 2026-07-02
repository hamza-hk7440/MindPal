from uuid import UUID

from chat.application.services.get_first_message_service import IGetFirstMessageService
from chat.domain.interfaces.conversation_repo import IConversationRepository
from chat.domain.interfaces.message_repo import IMessageRepository
from chat.application.exceptions.exception import ConversationCreationFailureException
class GetFirstMessageService(IGetFirstMessageService):
    def __init__(self, message_repo: IMessageRepository, conversation_repo: IConversationRepository):
        self.message_repo = message_repo
        self.conversation_repo = conversation_repo

    async def get_first_message(self, subject_id: UUID) -> str:
        conversations = await self.conversation_repo.get_conversations_by_subject_id(subject_id, skip=0, limit=1)
        if not conversations:
            raise ConversationCreationFailureException(f"No conversations found for subject ID {subject_id}.")

        first_conversation = conversations[0]
        messages = await self.message_repo.get_messages_by_conversation_id(first_conversation.id, skip=0, limit=1)
        if not messages:
            raise ConversationCreationFailureException(
                f"No messages found for subject ID {subject_id} in conversation {first_conversation.id}."
            )
        return messages[0].content
