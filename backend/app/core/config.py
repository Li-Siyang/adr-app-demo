from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from the environment."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://adr:adr@localhost:5432/adr"

    sso_issuer: str = ""
    sso_audience: str = ""
    sso_jwks_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
