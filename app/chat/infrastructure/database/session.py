from collections.abc import AsyncIterator

from supabase import AsyncClient, create_async_client

from chat.infrastructure.config.settings import settings

_supabase_client: AsyncClient | None = None


async def _get_or_create_supabase_client() -> AsyncClient:
    global _supabase_client

    if _supabase_client is None:
        _supabase_client = await create_async_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY,
        )

    return _supabase_client


async def init_chat_db() -> AsyncClient:
    return await _get_or_create_supabase_client()


async def get_supabase_client() -> AsyncIterator[AsyncClient]:
    yield await _get_or_create_supabase_client()
