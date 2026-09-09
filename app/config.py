"""Application configuration settings."""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic environment settings for backend."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


    PROJECT_NAME: str = "Smart Glasses LLM Controller"
    VERSION: str = "1.0.0"

    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    TEMPERATURE: float = 0.2

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "info"


settings = Settings()

