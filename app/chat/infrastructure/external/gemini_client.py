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
        Your answer will be provided based on the following relevant chunks from the course materials. Use the best matching information from those chunks to answer the student's question.
        Be flexible with abbreviations, spelling mistakes, short forms, and partial terms. For example, if the student asks "what's is bi" and the context mentions BI, Business Intelligence, dashboards, data analysis, reporting, or decision support, treat that as relevant and answer from the context.
        Only use the fallback when the retrieved context is empty or completely unrelated to the student's question. Do not reject a question just because the exact words are not repeated.
        And always provide the user with simple and daily examples to make him imagine the situation and understand the answer better.
        In addition, be gentle with students and behave like a teacher who is trying to help his students understand the course materials better.
        Try always to give students advice on how to study and understand the course materials better.
        If you feel that the student is struggling with the course materials, provide them with some study tips and advice on how to improve their understanding of the subject and don't forget to always motivate them.
        
        Retrieved Textbook Context:
        {cleaned_context}

        Answer style:
        1) Use clean Markdown formatting with short paragraphs, headings, and bullet points when helpful.
        2) Do not start with a long greeting. Begin with a direct answer to: "{message}".
        3) Keep the answer concise, friendly, and grounded in the relevant chunks provided above. You may connect ideas across chunks and explain them in simpler words.
        4) Explain concepts simply and include one daily-life analogy when it helps.
        5) If useful, add a small "Example" section or a Markdown table.
        6) If the student should search for more, suggest exact YouTube search keywords only, not raw URLs.
        7) End with a short "Quick recap" section and one natural next question the student can ask.

        Important: Do not invent facts that contradict the retrieved chunks. If the chunks are related, answer using them even when the match is not exact.
        If the context is empty or completely unrelated, respond in this format:
        **Not found in your documents**
        Your current documents don't underline this detail.

        **What you can do next**
        - Upload a document or slide that explains this term.
        - Ask me about another concept from the current documents.
        - Search YouTube for: "[the student's term] course explanation"

        **Quick recap**
        I can't confirm this from your uploaded material yet, but I can help once the right document is added.
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
