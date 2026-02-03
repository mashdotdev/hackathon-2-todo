"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    DATABASE_URL: str = "postgresql://localhost/todo"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    FRONTEND_URL: str = "https://hackathon-2-todo-seven.vercel.app/"

    # Environment
    ENVIRONMENT: str = "development"

    # Phase III: AI Chatbot - Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini/gemini-2.5-flash"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"


settings = Settings()
