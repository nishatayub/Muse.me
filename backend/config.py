"""
Application configuration and environment variable management.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    openrouter_api_key: str
    spotify_client_id: str
    spotify_client_secret: str
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    replicate_api_token: Optional[str] = None

    # App Settings
    environment: str = "production"
    debug: bool = False
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
