from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH: Path = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_NAME: str
    DB_HOST: str
    DB_PORT: int

    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str
    APP_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=ENV_PATH / ".env", env_file_encoding="utf-8"
    )


settings = Settings()
