from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Manages application settings and configurations."""

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/fireguard"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
