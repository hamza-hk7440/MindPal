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
