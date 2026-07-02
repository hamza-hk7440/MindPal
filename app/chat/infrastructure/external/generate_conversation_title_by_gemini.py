from chat.application.services.conversation_title_service_by_gemini import IConversationTitleServiceByGemini
import google.generativeai as genai

class ConversationTitleServiceByGemini(IConversationTitleServiceByGemini):
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    async def generate_conversation_title_by_gemini(self, conversation_id: str, message: str) -> str:
        formatted_prompt = f"""
        You are an AI assistant that generates a concise and relevant title for a conversation based on the provided message. 
        The title should be no more than 10 words, capturing the essence of the conversation. 
        Ensure the title is clear, engaging, and accurately reflects the content of the message.

        Conversation ID: {conversation_id}
        Message: {message}

        Please provide only the title in your response.
        """
        response = await self.model.generate_text(
            prompt=formatted_prompt)
        return response.text