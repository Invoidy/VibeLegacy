from pathlib import Path
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_URL: str
    API_KEY: str
    MODEL: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env"
    )

try:
    settings = Settings()
except Exception as e:
    env_folder = Path(__file__).resolve().parent
    os.startfile(env_folder)
    print("Error in env file. Pls configure it")
    raise e