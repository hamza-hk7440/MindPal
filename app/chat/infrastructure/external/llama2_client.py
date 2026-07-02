from email import message

from chat.application.services.llama2_service import ILlama2Service
from chat.infrastructure.config.settings import settings

import httpx


class Llama2Client(ILlama2Service):
    async def serialize_fetch_messages(self, chat_history: list) -> str:
        """
        Serialize the chat history into a string format.
        """
        serialized_history = ""
        for message in chat_history:
            serialized_history += f"{message.sender.value}: {message.content}\n"
        return serialized_history.strip()
    async def send_message_to_llama2(self, cleaned_context: str, conversation_id: str, message: str, chat_history: list) -> str:
        chat_history_as_string = await self.serialize_fetch_messages(chat_history)
        formatted_prompt=f"""
        You are an AI assistant helping students with their course materials.
        If the student asks a question depends on previous discussions with you in the conversation, you should consider the previous messages in the conversation to provide a more accurate and helpful answer.
        Chat History:
        {chat_history_as_string}
        Your answer will be provided based on the following relevant chunks from the course materials, provide a concise and informative response to the user's question.
        Also, if the relevant chunks do not contain enough information to answer the question, please respond with "Your current documents don't underline this detail." Do not make up answers or provide information that is not present in the relevant chunks.
        And always provide the user with simple and daily examples to make him imagine the situation and understand the answer better.
        In addition, be gentle with students and behave like a teacher who is trying to help his students understand the course materials better.
        Try always to give students advice on how to study and understand the course materials better.
        If you feel that the student is struggling with the course materials, provide them with some study tips and advice on how to improve their understanding of the subject and don't forget to always motivate them.
        
        Retrieved Textbook Context:
        {cleaned_context}

        Answer style:
        1) Start your answer with a friendly greeting and a motivational message to the student.
        2) Acknowledge the student's question directly: "{message}".
        3) Provide a concise and informative response to the user's question based strictly on the relevant chunks provided above.
        4) Explain every concept in a simple and easy to understand way, and provide daily physical analogies to help them visualize it.
        5) If possible, use a Markdown table to clarify or compare concepts.
        6) If a student wants to learn more, suggest the exact search keywords they should type into YouTube to find good video lectures (Do NOT try to generate or write out raw URLs/links).
        7) Provide the student with opening questions to bridge them into the next logical concept of the subject and motivate them to explore further.
        8) Even if the subject is dry, make it lively and physical so they can imagine it and stay engaged.
        9) End with a solid summary conclusion and a powerful motivational message to encourage them to keep pushing forward.

        Important: Do not make up answers or provide information that is not present in the relevant chunks. If the relevant chunks do not contain enough information to answer the question, please respond with "Your current documents don't underline this detail."
        """
        payload = {
            "model": "llama2",
            "prompt": formatted_prompt,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post("http://127.0.0.1:11434/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")