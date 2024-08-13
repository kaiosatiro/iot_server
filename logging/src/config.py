from typing import Literal
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, model_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    ENVIRONMENT: Literal["dev", "staging", "production"] = "dev"
    LOG_LEVEL: str = "INFO"
    LOG_INFO_LOCAL_PATH: str = "/src/logs/"  # 'path' may conflict
    PYTHONPATH: str

    @computed_field  # type: ignore
    @property
    def LOG_INFO_FILE(self) -> str:
        path = Path(self.LOG_INFO_LOCAL_PATH).joinpath("logging_service_logs.log")
        return str(path).strip(r'\/')
    
    RABBITMQ_DNS: str = "localhost"
    RABBITMQ_PORT: int = 5672
    # RABBITMQ_USER: str = "guest"
    # RABBITMQ_PASSWORD: str = "guest"

    MESSAGES_EXCHANGE: str = "messages"
    MESSAGES_QUEUE: str = "messages"
    MESSAGES_ROUTING_KEY: str = "messages.receiver"


settings = Settings()
