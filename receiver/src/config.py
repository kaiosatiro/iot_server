import secrets
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    ENVIRONMENT: Literal["dev", "staging", "production"] = "dev"
    LOG_LEVEL: str = "INFO"

    PROJECT_NAME: str = "iot-api"
    DOMAIN: str = "localhost"
    RECEIVER_API_V1_STR: str = "/listener/v1"
    RECEIVER_VERSION: str = "0.1.0"

    SECRET_KEY: str = secrets.token_urlsafe(32)

    RABBITMQ_DNS: str = "localhost"
    RABBITMQ_PORT: int = 5672
    # RABBITMQ_USER: str = "guest"
    # RABBITMQ_PASSWORD: str = "guest"

    MESSAGES_EXCHANGE: str = "messages"
    MESSAGES_QUEUE: str = "messages"
    MESSAGES_ROUTING_KEY: str = "messages.receiver"
    MESSAGES_DECLARE_EXCHANGE: bool = True

    ALGORITHM: str = "HS256"

settings = Settings()

if __name__ == "__main__":
    print(settings.dict())
