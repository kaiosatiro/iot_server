from pathlib import Path
from typing import Literal, Self

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    ENVIRONMENT: Literal["dev", "staging", "production"] = "dev"
    LOG_LEVEL: str = "INFO"
    LOG_INFO_LOCAL_PATH: str
    LOG_FILE_MAX_SIZE: int = 10240
    LOG_FILE_BACKUP_COUNT: int = 5

    REMOTE_LOG_HANDLER_NAME: str = "remoteSysLog"
    REMOTE_LOG_LEVEL: str = "WARNING"
    REMOTE_LOG_ADDRESS: str | None = None
    REMOTE_LOG_PORT: int | None = None

    @computed_field  # type: ignore
    @property
    def ENABLE_REMOTE_LOG(self) -> bool:
        return self.REMOTE_LOG_ADDRESS is not None and self.REMOTE_LOG_PORT is not None

    @model_validator(mode="after")
    def _set_default_REMOTE_LOG_config(self) -> Self:
        if self.REMOTE_LOG_ADDRESS is None and self.REMOTE_LOG_PORT is None:
            self.REMOTE_LOG_ADDRESS = "localhost"
            self.REMOTE_LOG_PORT = 514
        return self

    @computed_field  # type: ignore
    @property
    def LOG_INFO_FILE(self) -> str:
        path = Path(self.LOG_INFO_LOCAL_PATH).joinpath("logging_service_logs.log")
        # For testing outside the container it needs a relative path on .env
        return str(path)

    TIME_SERVICE_UPDATE_INTERVAL: int = 60

    RABBITMQ_DNS: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    LOG_EXCHANGE: str
    LOG_QUEUE: str

    @computed_field  # type: ignore
    @property
    def LOG_ROUTING_KEY(self) -> str:
        return f"{self.LOG_EXCHANGE}.*"

    RECEIVER_ID: str
    HANDLER_ID: str
    USERAPI_ID: str


settings = Settings()
