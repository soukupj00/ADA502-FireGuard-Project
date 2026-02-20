from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Manages application settings and configurations."""

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/fireguard"

    class Config:
        """Pydantic-settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
