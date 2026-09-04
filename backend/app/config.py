from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://key3in:key3in@postgres:5432/key3in"
    base_path: str = "/key3in"
    cors_origins: list[str] = ["https://kvasmix.ru"]
    max_note_length: int = 20_000
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("base_path")
    @classmethod
    def normalize_base_path(cls, value: str) -> str:
        value = value.strip()
        return "/" + value.strip("/") if value.strip("/") else ""

@lru_cache
def get_settings() -> Settings:
    return Settings()
