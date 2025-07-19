from pydantic_settings import BaseSettings
from typing import List, Union


class Settings(BaseSettings):
    PROJECT_NAME: str = "Research Analytics Platform"
    API_V1_STR: str = "/api/v1"
    
    # CORS origins for frontend communication
    # In production, you would replace "*" with your actual frontend domain.
    BACKEND_CORS_ORIGINS: List[Union[str, any]] = ["*"]
    
    class Config:
        case_sensitive = True


settings = Settings()

