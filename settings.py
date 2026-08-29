import os
from pathlib import Path
from pydantic import StringConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated

NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]

class Settings(BaseSettings):
    BASE_URL: NonEmptyStr
    API_KEY: NonEmptyStr
    MODEL: NonEmptyStr

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".CONFIG_ME"

    )

try:
    settings = Settings()
except Exception as e:
    print("!!!\n\n\n\n Error in '.CONFIG_ME' file. Pls configure it \n\n\n\n!!!")
    env_folder = Path(__file__).resolve().parent
    os.startfile(env_folder)
    exit()