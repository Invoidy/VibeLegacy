from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_URL: str
    API_KEY: str
    MODEL: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env"
    )


settings = Settings()
