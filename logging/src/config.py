from pathlib import Path
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    ENVIRONMENT: Literal["dev", "staging", "production"] = "dev"
    LOG_LEVEL: str = "INFO"
    LOG_INFO_LOCAL_PATH: str = "/temp/"  # 'path' may conflict

    @computed_field  # type: ignore
    @property
    def LOG_INFO_FILE(self) -> str:
        path = Path(self.LOG_INFO_LOCAL_PATH).joinpath("logging_service_logs.log")
        return str(path)

    TIME_SERVICE_UPDATE_INTERVAL: int = 60

    RABBITMQ_DNS: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    LOG_EXCHANGE: str = "logs"
    LOG_QUEUE: str = "logs"
    LOG_ROUTING_KEY: str = "log.*"

    RECEIVER_ID: str = "receiver"
    HANDLER_ID: str = "handler"
    USERAPI_ID: str = "userapi"


settings = Settings()
