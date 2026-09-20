# 🧠 MindPal

MindPal is an advanced, event-driven AI-powered learning platform designed to help students master subjects by transforming any course material—including **PDFs, YouTube videos, images, audio, and lessons**—into interactive learning experiences complete with an AI tutor, Retrieval-Augmented Generation (RAG), and auto-generated quizzes.

---

## 🏗️ Architectural Overview

MindPal is structured using a strict **Modular Clean Architecture**, separating domain logic, application use cases, infrastructure, and presentation layers across independent modules (`Chat`, `Ingestion`, `Assessment`, and `Users`). 

To handle heavy workloads smoothly, the system uses an **Event-Driven Architecture (Pub/Sub)** powered by **Redis** and **Celery**, ensuring that heavy operations (like parsing, chunking, and vectorizing documents) never block the main FastAPI server thread.

### Key Architectural Highlights:
- **Asynchronous Background Processing:** Celery and Redis manage background ingestion workers reliably.
- **Decoupled Event Bus:** Modules communicate asynchronously via Redis Pub/Sub channels (e.g., conversation creation triggers automated resource chunking).
- **Real-Time Capabilities:** WebSockets provide live progress tracking for long-running ingestion tasks and streaming token responses for the AI chat tutor.
- **RAG Pipeline:** Integrates vector search to feed precise, document-derived context directly into LLM prompts.

---

## 🚀 Core Features

- **Multi-Format Ingestion:** Upload or link study materials across diverse formats (PDF, YouTube, audio, images, lessons).
- **Smart Chunking & Vectorization:** Automatically splits documents and indexes them into a vector database for semantic search.
- **AI Tutor Chat:** Streamed, real-time conversational responses powered by RAG context.
- **Assessment & Quizzes:** Auto-generated practice quizzes to test knowledge retention.
- **Live Progress Tracking:** Monitor background ingestion and processing status via WebSockets.

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Task Queue & Broker:** Celery, Redis
- **Database & Storage:** Supabase (Async/Sync clients)
- **Vector Search:** ChromaDB, FastEmbed
- **Real-time:** WebSockets

### Frontend
- **Framework:** React / Modern UI
- **Features:** Interactive dashboards, file upload managers, chat interface, and quiz modules.

---