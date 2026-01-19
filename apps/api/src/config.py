from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator
from typing import Optional, Any
import secrets


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "Legal Assistant AI"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # Object Storage (S3/MinIO)
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str = "legal-documents"
    S3_REGION: str = "us-east-1"

    # JWT
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.2

    # Anthropic
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    ANTHROPIC_MAX_TOKENS: int = 4096

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # CORS
    CORS_ORIGINS: Any = "http://localhost:3000,https://localhost:3002"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS_ORIGINS from comma-separated string."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # File Upload
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB
    ALLOWED_FILE_TYPES: Any = "pdf,docx,doc,txt"
    
    @field_validator('ALLOWED_FILE_TYPES', mode='before')
    @classmethod
    def parse_file_types(cls, v: Any) -> list[str]:
        """Parse ALLOWED_FILE_TYPES from comma-separated string."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        elif isinstance(v, list):
            return v
        return ["pdf", "docx", "doc", "txt"]

    # Encryption
    ENCRYPTION_KEY: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"


settings = Settings()
