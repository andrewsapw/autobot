import os
import pathlib

from dotenv import load_dotenv
from pydantic import BaseSettings

ROOT_DIR = pathlib.Path(__file__).parent

load_dotenv(ROOT_DIR.parent / ".env")
BOT_TOKEN: str = os.environ.get("BOT_TOKEN", None)


class Settings(BaseSettings):
    APP_NAME: str = "AutoBot"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore
