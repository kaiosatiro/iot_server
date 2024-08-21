import secrets
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    ENVIRONMENT: Literal["dev", "staging", "production"] = "dev"
    LOG_LEVEL: str = "INFO"

    PROJECT_NAME: str = "..."
    DOMAIN: str = "localhost"
    RECEIVER_API_V1_STR: str = "/listener/v1"
    RECEIVER_VERSION: str = "0.1.0"

    SECRET_KEY: str = secrets.token_urlsafe(32)

    RABBITMQ_DNS: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    RECEIVER_ID: str

    MESSAGES_EXCHANGE: str
    MESSAGES_QUEUE: str
    MESSAGES_DECLARE_EXCHANGE: bool = True

    @computed_field  # type: ignore
    @property
    def MESSAGES_ROUTING_KEY(self) -> str:
        return f"{self.MESSAGES_EXCHANGE}.{self.RECEIVER_ID}"

    LOG_EXCHANGE: str
    LOG_QUEUE: str

    @computed_field  # type: ignore
    @property
    def LOG_ROUTING_KEY(self) -> str:
        return f"{self.LOG_EXCHANGE}.{self.RECEIVER_ID}"

    ALGORITHM: str = "HS256"


settings = Settings()
