import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    Loads variables from a .env file and the environment.
    This provides a centralized and type-safe way to handle configuration.
    """
    # --- Project Metadata ---
    PROJECT_NAME: str = "Intelligent Backend Service"
    API_V1_STR: str = "/api/v1"

    # --- Database Configuration ---
    # The DATABASE_URL is constructed to be compatible with SQLAlchemy.
    # Example for PostgreSQL: "postgresql://user:password@host:port/database"
    # Example for SQLite: "sqlite:///./intelligent_backend.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./intelligent_backend.db")

    # --- External Service API Keys ---
    # It's crucial to load secrets from the environment, not hardcode them.
    OPENAI_API_KEY: str

    # --- Burr and Workflow Settings ---
    # Add any Burr-specific configurations here if needed.

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True, # Important for environment variables
        extra='ignore'
    )

# Create a single, importable instance of the settings.
# This instance will be used throughout the application to access config values.
settings = Settings()
