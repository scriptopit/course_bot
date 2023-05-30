import os

from loguru import logger
from pydantic import BaseSettings
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


class Settings(BaseSettings):
    STAGE: str = "LOCAL"
    LOGGING_LEVEL: int = 20
    TELEBOT_TOKEN: str = ""
    DB_KEY_VALIDATION: str = ""
    BASE_API_URL: str = "http://cryptopayments:8000"
    ADMINS: list = [2113806246]
    DEBUG: bool = False


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")


DEBUG: bool = settings.DEBUG
STAGE: str = settings.STAGE
DB_KEY_VALIDATION: str = settings.DB_KEY_VALIDATION
BASE_API_URL: str = settings.BASE_API_URL


admins_list: list = settings.ADMINS

TOKEN_BOT: str = os.getenv("TELEBOT_TOKEN")
bot = Bot(token=TOKEN_BOT)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")


KICK_RATE = int(os.getenv("KICK_RATE", 20))
HELP_RATE = int(os.getenv("HELP_RATE", 10))
# HELPERS_CHAT = int(os.getenv("HELPERS_CHAT"))
HELPERS_CHAT: int = -1001646837206
