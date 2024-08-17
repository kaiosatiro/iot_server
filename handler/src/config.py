from typing import Literal

from pydantic import computed_field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    ENVIRONMENT: Literal["dev", "staging", "production"] = "dev"
    LOG_LEVEL: str = "INFO"

    RABBITMQ_DNS: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    LOG_EXCHANGE: str
    LOG_QUEUE: str

    HANDLER_ID: str

    MESSAGES_EXCHANGE: str
    MESSAGES_QUEUE: str
    MESSAGES_DECLARE_EXCHANGE: bool = True

    @computed_field  # type: ignore
    @property
    def LOG_ROUTING_KEY(self) -> str:
        return f"{self.LOG_EXCHANGE}.{self.HANDLER_ID}"

    @computed_field  # type: ignore
    @property
    def MESSAGES_ROUTING_KEY(self) -> str:
        return f"{self.MESSAGES_EXCHANGE}.{self.HANDLER_ID}"

    # Postgres Config
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field  # type: ignore
    @property
    def SQL_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
