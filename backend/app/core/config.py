from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "cramCortex"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:8002",
        "http://127.0.0.1:8002"
    ]
    
    # File upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    
    # ML Models
    SENTENCE_TRANSFORMER_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Database
    DATABASE_URL: str = "sqlite:///./cramcortex.db"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"  # More reliable than gpt-3.5-turbo for constraint following
    OPENAI_MAX_TOKENS: int = 3000  # Increased for longer translations
    OPENAI_TEMPERATURE: float = 0.0  # ZERO randomness for strict constraint adherence
    
    class Config:
        env_file = ".env"


settings = Settings()