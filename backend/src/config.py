from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Manages application settings and configurations."""

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/fireguard"
    REDIS_URL: str = "redis://localhost:6379/0"

    # HiveMQ MQTT Broker Settings
    HIVEMQ_HOST: str = "hivemq"  # Default to the service name in docker-compose
    HIVEMQ_PORT: int = 1883  # Standard MQTT port

    # ThingSpeak API Settings
    THINGSPEAK_API_KEY: str = ""  # ThingSpeak Write API Key

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
