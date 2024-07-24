from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    PostgresDsn,
    computed_field,
)
from pydantic_core import MultiHostUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    # API_V1_STR: str = "/api/v1"
    # SECRET_KEY: str = token_urlsafe(32)
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # DOMAIN: str = "localhost"
    # ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PROJECT_NAME: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "app"

    @computed_field
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

    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_NAME: str
    FIRST_SUPERUSER_PASSWORD: str
    # USERS_OPEN_REGISTRATION: bool = False

    # def _check_default_secret(self, var_name: str, value: str | None) -> None:
    #     if value == "changethis":
    #         message = (
    #             f'The value of {var_name} is "changethis", '
    #             "for security, please change it, at least for deployments."
    #         )
    #         if self.ENVIRONMENT == "local":
    #             warn(message, stacklevel=1)
    #         else:
    #             raise ValueError(message)

    # @model_validator(mode="after")
    # def _enforce_non_default_secrets(self) -> Self:
    #     self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
    #     self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
    #     self._check_default_secret(
    #         "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
    #     )

    #     return self


settings = Settings()

if __name__ == "__main__":
    print(settings.dict())
    print(settings.SQLALCHEMY_DATABASE_URI)
