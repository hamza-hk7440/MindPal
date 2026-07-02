# Chat Module Handoff

## Purpose
The `chat` module implements the conversation and message flow for MindPal. It follows a layered structure:

- `domain`: core business rules, entities, value objects, events, and repository interfaces
- `application`: use cases, DTOs, and service abstractions
- `infrastructure`: database models, repository implementations, external AI clients, and runtime settings
- `presentation`: API layer, currently only package scaffolding

This document is meant to help another assistant continue the work without re-discovering the module from scratch.

## High-Level Responsibilities

The module appears to support:

- creating conversations for a subject
- saving user messages
- generating AI responses to messages
- fetching messages by conversation
- generating conversation titles from the first message
- dispatching domain/application events after important actions

## Folder Map

### `domain/`
Contains the core chat rules and contracts.

#### `entities/`
- `conversation.py`: conversation entity with `id`, `subject_id`, `title`, and optional `created_at`
- `message.py`: message entity with `id`, `conversation_id`, `content`, `sender`, and optional `created_at`

#### `value_objects/`
- `message_objects.py`: defines `Role` enum with `USER` and `AI`

#### `events/`
- `base.py`: base `DomainEvent`
- `conversation_event.py`: `ConversationCreatedEvent`
- `messages_events.py`: `SendMessageEvent` and `GetAllMessagesEvent`

#### `exceptions/`
- `domain_exceptions.py`: common domain exception types

#### `interfaces/`
- `base.py`: generic repository interface
- `conversation_repo.py`: conversation repository contract
- `message_repo.py`: message repository contract
- `events.py`: event dispatcher contract

### `application/`
Contains use cases, DTOs, and service abstractions.

#### `dtos/`
- `conversation_dto.py`: API-facing conversation data shape
- `message_dto.py`: API-facing message data shape

#### `exceptions/`
- `exception.py`: chat application exceptions

#### `services/`
- `get_first_message_service.py`: abstraction for extracting the first message
- `conversation_title_service_by_gemini.py`: abstraction for Gemini-based title generation
- `conversation_title_service_by_llama2.py`: abstraction for Llama2-based title generation
- `gemini_service.py`: abstraction for Gemini message generation
- `llama2_service.py`: abstraction for Llama2 message generation

#### `use_cases/commands/`
- `create_conversation.py`: creates a conversation, generates a title, saves it, dispatches an event
- `send_message_uc.py`: validates and saves a user message, dispatches an event
- `generate_response_uc.py`: generates an AI reply, saves it, dispatches an event

#### `use_cases/queries/`
- `fetch_message.py`: fetches messages for a conversation and dispatches a retrieval event

### `infrastructure/`
Contains concrete implementations for persistence, configuration, and external services.

#### `config/`
- `settings.py`: environment-driven app settings

#### `database/`
- `base.py`: SQLAlchemy base
- `models/`: ORM models for conversations and messages
- `repositories/`: SQLAlchemy repository implementations
- `migrations/`: migration package placeholder

#### `external/`
- `gemini_client.py`: concrete Gemini message generator
- `llama2_client.py`: concrete Llama2 message generator
- `generate_conversation_title_by_gemini.py`: Gemini title generator
- `generate_conversation_title_by_llama2.py`: Llama2 title generator
- `get_first_message.py`: implementation of first-message lookup

### `presentation/`
Contains the API layer scaffolding.

- `controllers/`: should hold request handlers
- `routes/`: should map endpoints to controllers
- `schemas/`: should define request/response schemas
- `middleware/`: should hold auth, logging, or other HTTP cross-cutting logic

## Main Flow

### 1. Create Conversation

Expected flow:

1. A caller requests conversation creation for a `subject_id`
2. The system retrieves the first message for the conversation context
3. A title is generated using either Gemini or Llama2 depending on environment
4. A `Conversation` entity is created
5. The conversation is saved through the repository
6. `ConversationCreatedEvent` is dispatched
7. A `ConversationDTO` is returned

### 2. Send Message

Expected flow:

1. Validate message content and sender
2. Confirm the conversation exists
3. Create a `ChatMessage` entity
4. Save it through the repository
5. Dispatch `SendMessageEvent`
6. Return `MessageDTO`

### 3. Generate AI Response

Expected flow:

1. Validate input and conversation existence
2. Use environment to choose Gemini or Llama2
3. Ask the model to generate a reply
4. Save the AI response as a `ChatMessage`
5. Dispatch `SendMessageEvent`
6. Return `MessageDTO`

### 4. Fetch Messages

Expected flow:

1. Confirm the conversation exists
2. Fetch messages by conversation ID
3. Dispatch `GetAllMessagesEvent`
4. Return the messages

## Important Dependencies

- `IConversationRepository` and `IMessageRepository` are the core persistence contracts
- `IEventDispatcher` is used after creating conversations and messages
- `IGeminiService` and `ILlama2Service` abstract AI reply generation
- `IConversationTitleServiceByGemini` and `IConversationTitleServiceByLlama2` abstract title generation
- `IGetFirstMessageService` abstracts retrieval of the first message
- `settings.ENVIRONMENT` controls whether local or non-local AI services are used

## Observations And Risks

These are important for the next assistant to know:

1. `Conversation(id=None, ...)` and `ChatMessage(id=None, ...)` are created in use cases, but the domain entities currently appear to require `id` in the dataclass signature. That may cause construction issues unless the actual local file differs or default handling exists elsewhere.
2. `create_conversation.py` calls `get_first_message(conversation_id=None)`, which looks inconsistent because the service expects a `conversation_id`.
3. `CreateConversationUseCase` uses `conversation_title_service_by_gemini.generate_conversation_title_by_gemini(message=first_message)`, but the implementation file appears to expect additional arguments in some versions.
4. `SendMessageUseCase` injects `IGeminiService` as `message_service`, but the current method body does not use it.
5. `GenerateResponseUseCase` chooses between AI providers based on environment, but the imported services and method names should be checked for consistency.
6. The repository implementations and ORM models should be reviewed carefully for SQLAlchemy correctness, especially column definitions and relationship mapping.
7. `presentation/` is still empty apart from `__init__.py`, so no HTTP endpoints are wired yet.

## Likely Next Work

If continuing implementation, the next assistant will probably need to:

- stabilize the domain constructors and IDs
- align service interfaces with their concrete implementations
- fix repository/model mismatches
- implement presentation controllers, routes, and schemas
- decide how events are dispatched and consumed

## Suggested Handoff Summary

The chat module already has the main architectural layers and use cases sketched out, but several contracts and implementations appear inconsistent. The next step should be to reconcile the interfaces, entities, and infrastructure implementations before wiring the presentation layer.
