"""
ClipoAI Backend Configuration.

Loads settings from environment variables with sensible defaults.
Uses Pydantic Settings for validation and type safety.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "ClipoAI"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-to-a-random-secret-key"

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8080
    allowed_origins: str = "http://localhost,http://localhost:5173,http://localhost:80"

    # Database
    database_url: str = "postgresql+asyncpg://clipoai:clipoai_dev_password@postgres:5432/clipoai"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_root_user: str = "clipoai"
    minio_root_password: str = "clipoai_minio_password"
    minio_bucket: str = "clipoai-videos"
    minio_use_ssl: bool = False

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333

    # JWT
    jwt_secret_key: str = "change-me-to-a-random-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # YouTube
    youtube_api_key: str = ""

    # AI / LLM
    gemini_api_key: str = ""

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Singleton settings instance
settings = Settings()
