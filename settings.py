import os
from pathlib import Path
from pydantic import StringConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated
import shutil
from utils import check_if_first_start

if check_if_first_start():
    with open(Path(__file__).resolve().parent / ".CONFIG_ME", "w") as config_file:
        config_file.write("""BASE_URL=https://openrouter.ai/api/v1
API_KEY=
MODEL=openai/gpt-5.6-luna
REASONING=""")

    print("\n" + "=" * shutil.get_terminal_size().columns, end="")
    print("""Welcome to VibeLegacy!

    Before you start, configure the `.CONFIG_ME` file with your API settings.

    You can view all available commands with `/help`.

    Main commands:

    * `/add <file>` — attach a file to the conversation
    * `/drop <file>` — remove an attached file
    * `/clear` — clear the message history

    Once configured, just describe what you want to build or change, and VibeLegacy will handle the code changes.

    Have fun vibing — with control.
    """)

    print("\n" + "=" * shutil.get_terminal_size().columns, end="")

    env_folder = Path(__file__).resolve().parent
    os.startfile(env_folder)
    exit(0)

NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]

class Settings(BaseSettings):
    BASE_URL: NonEmptyStr
    API_KEY: NonEmptyStr
    MODEL: NonEmptyStr
    REASONING: str | None

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