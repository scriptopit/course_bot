from pydantic import BaseSettings

from loguru import logger
from aiocryptopay import AioCryptoPay, Networks


class Settings(BaseSettings):
    SERVER_HOST: str = '0.0.0.0'
    SERVER_PORT: int = 8000
    DEBUG: bool = True
    ADMINS: list = [2113806246]
    TELEBOT_TOKEN: str
    DB_KEY_VALIDATION: str
    CRYPTO_PAY_KEY: str
    LOCATION: str = 'SERVER'


class Database(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    def get_db_name(self):
        return f"postgres://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


db = Database(
    _env_file='.env',
    _env_file_encoding='utf-8'
)

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
crypto = AioCryptoPay(token=settings.CRYPTO_PAY_KEY, network=Networks.MAIN_NET)

DATABASE_CONFIG = {
    "connections": {"default": db.get_db_name()},
    "apps": {
        "models": {
            "models": [
                "aerich.models",
                "cryptopayments.models.models"
            ],
            "default_connection": "default",
        },
    },
}
