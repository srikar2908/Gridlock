from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GRIDLOCK SENTINEL API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    mongodb_uri: str = Field(default="", description="MongoDB Atlas connection string.")
    database_name: str = "gridlock"
    groq_api_key: str = ""
    groq_primary_model: str = "llama-4-scout"
    groq_fallback_model: str = "qwen3-32b"
    redis_url: str = "redis://localhost:6379/0"
    enable_redis_cache: bool = True
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    jwt_secret: str = ""
    auth_required: bool = False
    allowed_roles: List[str] = ["admin", "operator", "analyst"]

    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    assets_dir: Path = Path("assets")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_environment(self):
        if self.app_env.lower() in {"production", "prod"} and not self.mongodb_uri:
            raise ValueError("MONGODB_URI is required in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
