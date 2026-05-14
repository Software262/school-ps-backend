import os
import sys
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_file() -> str:
    """Determine which env file to use based on environment"""

    if "pytest" in sys.modules:
        return ".env.test"

    if os.getenv("ENVIRONMENT") == "testing":
        return ".env.test"

    return ".env"


class Settings(BaseSettings):
    app_name: str = "school-ps"
    port: int = 8000
    version: str = "1.0.0"
    environment: str = "development"
    prefix_api: str = "/api/v1"
    database_url: str = "postgresql://postgres:password@localhost:5432/postgres"
    secret_key: str = ""
    algorithm: str = ""
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=get_env_file())


@lru_cache
def get_settings():
    return Settings()
