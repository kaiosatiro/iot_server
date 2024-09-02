import secrets
from typing import Literal, Self

from pydantic import PostgresDsn, computed_field, model_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    ENVIRONMENT: Literal["dev", "staging", "production"] = "dev"
    LOG_LEVEL: str = "INFO"

    PROJECT_NAME: str = "..."
    DOMAIN: str = "localhost"

    USERAPI_API_V1_STR: str = ""
    RECEIVER_API_V1_STR: str = ""  # for the documentation only
    VERSION: str = "0.1.0"

    USERS_OPEN_REGISTRATION: bool = False

    SECRET_KEY: str = secrets.token_urlsafe(
        32
    )  # TODO: change it according to the environment

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # seven days
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48  # 48 hours

    INSERT_EXAMPLE_DATA: bool = False  # TODO: change it according to the environment

    @computed_field  # type: ignore
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "dev":
            return f"http://{self.DOMAIN}:8000"
        elif self.ENVIRONMENT == "staging":
            return f"https://staging.{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    # DB | Queue
    FIRST_SUPERUSER_EMAIL: (
        str  # TODO: update type to EmailStr when sqlmodel supports it
    )
    FIRST_SUPERUSERNAME: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_EMAIL: str

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

    # RabbitMQ Config
    RABBITMQ_DNS: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    # Logs channel config
    LOGGING_EXCHANGE: str
    LOG_QUEUE: str
    USERAPI_ID: str

    # Rpc channel config
    RPC_QUEUE: str
    RPC_TIMEOUT: int = 3

    @computed_field  # type: ignore
    @property
    def LOG_ROUTING_KEY(self) -> str:
        return f"{self.LOGGING_EXCHANGE}.{self.USERAPI_ID}"

    @computed_field  # type: ignore
    @property
    def RPC_ROUTING_KEY(self) -> str:
        return self.RPC_QUEUE

    # Email Config
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False

    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    EMAILS_FROM_EMAIL: str | None = (
        None  # TODO: update type to EmailStr when sqlmodel supports it
    )

    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    @computed_field  # type: ignore
    @property
    def emails_enabled(self) -> bool:
        return bool(
            self.SMTP_HOST and self.EMAILS_FROM_EMAIL
        )  # (self.EMAILS_FROM_EMAIL != "test@email.com")


settings = Settings()

if __name__ == "__main__":
    print(settings.dict())
