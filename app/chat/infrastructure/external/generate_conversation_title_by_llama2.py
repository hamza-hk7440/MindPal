from chat.application.services.conversation_title_service_by_llama2 import IConversationTitleServiceByLlama2
from chat.infrastructure.config.settings import settings
from groq import Groq
class ConversationTitleServiceByLlama2(IConversationTitleServiceByLlama2):
    def __init__(self):
        self.client=Groq(api_key=settings.GROQ_API_KEY)
        self.model_name="llama2-13b-chat"
    async def generate_conversation_title_by_llama2(self, conversation_id: str, message: str) -> str:
        formatted_prompt = f"""
        You are an AI assistant that generates a concise and relevant title for a conversation based on the provided message. 
        The title should be no more than 10 words, capturing the essence of the conversation. 
        Ensure the title is clear, engaging, and accurately reflects the content of the message.

        Conversation ID: {conversation_id}
        Message: {message}

        Please provide only the title in your response.
        """
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": formatted_prompt}
            ]
        )
        return response.choices[0].message.content