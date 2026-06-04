from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "cashmanager-api"
    app_env: str = "local"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Supabase — service role is backend-only (bypasses RLS).
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # OpenAI — optional; only used if the project has AI features.
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4-mini"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @cached_property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
