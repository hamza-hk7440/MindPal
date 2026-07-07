# chat/infrastructure/external/gemini_client.py

from google import genai
from google.genai import errors
from fastapi import status, HTTPException
from typing import AsyncGenerator

from chat.application.services.gemini_service import IGeminiService
from chat.infrastructure.config.settings import settings


class GeminiClient(IGeminiService):
    def __init__(self):
        # Migrated to the modern google-genai initialization engine
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model = "gemini-2.5-flash"  # Production grade lightweight model perfect for low-latency streaming

    async def serialize_fetch_messages(self, messages: list) -> str:
        """
        Serializes a list of messages into a string format suitable for the Gemini model.
        Each message is formatted as "Role: Content" and separated by newlines.
        """
        serialized_messages = []
        for message in messages:
            # Safely handle both standard DTO objects and orm attributes
            role = message.sender.value if hasattr(message.sender, 'value') else str(message.sender)
            content = message.content
            serialized_messages.append(f"{role}: {content}")
        return "\n".join(serialized_messages)

    def _build_system_prompt(self, cleaned_context: str, chat_history_as_string: str, message: str) -> str:
        """Helper to centralize your strict academic prompt rules."""
        return f"""
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

    async def send_message_to_gemini(self, cleaned_context: str, conversation_id: str, message: str, chat_history: list) -> str:
        """Legacy synchronous endpoint wrapper migrated to new SDK signatures."""
        try:
            chat_history_as_string = await self.serialize_fetch_messages(chat_history)
            formatted_prompt = self._build_system_prompt(cleaned_context, chat_history_as_string, message)
            
            # Formatted under modern pluralized 'contents' parameter configuration rule
            response = self._client.models.generate_content(
                model=self._model,
                contents=formatted_prompt
            )
            return response.text
        except errors.APIError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Gemini API Exception: {str(exc)}"
            )

    async def stream_message_to_gemini(self, chunks: list[str], conversation_id: str, message: str, chat_history: list) -> AsyncGenerator[str, None]:
        """
        NEW: Streams chunk tokens directly from the Gemini model using the new generate_content_stream engine.
        """
        try:
            # Flatten array of text chunks into a readable continuous context string
            cleaned_context = "\n\n".join(chunks) if isinstance(chunks, list) else str(chunks)
            chat_history_as_string = await self.serialize_fetch_messages(chat_history)
            formatted_prompt = self._build_system_prompt(cleaned_context, chat_history_as_string, message)

            # Fire the active HTTP network stream connection bundle
            response_stream = self._client.models.generate_content_stream(
                model=self._model,
                contents=formatted_prompt
            )

            # Iterate over incoming text fragment buffers and pass them back up to the Controller layer
            for response_chunk in response_stream:
                if response_chunk.text:
                    yield response_chunk.text

        except errors.APIError as exc:
            yield f"\n[ERROR: Gemini streaming generation aborted: {str(exc)}]"