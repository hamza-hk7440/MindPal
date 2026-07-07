import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")  # 3 levels up

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_path,
        env_ignore_empty=True,
        extra="ignore",)
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(..., env="SUPABASE_ANON_KEY")
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    ENVIRONMENT: str = Field(..., env="ENVIRONMENT")
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")
    USE_LOCAL_LLM: bool = Field(default=False, env="USE_LOCAL_LLM")
    DATABASE_URL: str | None = Field(default=None, env="DATABASE_URL")
    SUPABASE_CONVERSATIONS_TABLE: str = Field(default="Conversations", env="SUPABASE_CONVERSATIONS_TABLE")
    SUPABASE_MESSAGES_TABLE: str = Field(default="Messages", env="SUPABASE_MESSAGES_TABLE")
    SUPABASE_STUDY_SUBJECTS_TABLE: str = Field(default="Study_subject", env="SUPABASE_STUDY_SUBJECTS_TABLE")
    SUPABASE_RESOURCES_TABLE: str = Field(default="Sources", env="SUPABASE_RESOURCES_TABLE")
    SUPABASE_CHUNKS_TABLE: str = Field(default="Chunks", env="SUPABASE_CHUNKS_TABLE")

settings = Settings()
