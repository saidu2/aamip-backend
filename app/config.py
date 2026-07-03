from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/aamip"
    SECRET_KEY: str = "change_this_to_a_long_random_string_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    APP_NAME: str = "AAMIP"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5174"

    class Config:
        env_file = ".env"

settings = Settings()
