import os
import datetime
import asyncio

from config import bot, dp, DEBUG, logger, STAGE
from _recources import __build__, __appname__, __version__
from classes.errors_reporter import MessageReporter
from aiogram import executor
from keyboards.keyboards import StartMenu
from kicker.scheduler_funcs import check_base


async def on_startup(_) -> None:
    """Функция выполняющаяся при старте бота."""

    text: str = (
        f"{__appname__} started."
        f"\nBuild: {__build__}"
        f"\nVersion: {__version__}"
        f"\nStage: {STAGE}"
    )
    if DEBUG:
        text += "\nDEBUG = TRUE"
    try:
        await MessageReporter.send_report_to_admins(text=text, keyboard=StartMenu.keyboard())
    except Exception:
        pass
    if not os.path.exists('./db'):
        os.mkdir("./db")

    logger.info(f'Bot started at: {datetime.datetime.now()}'
                f'\nBOT POLLING ONLINE')
    asyncio.create_task(check_base())


async def on_shutdown(dp) -> None:
    """Действия при отключении бота."""
    try:
        await MessageReporter.send_report_to_admins(text=f"{__appname__} stopping.")
    except Exception:
        pass
    logger.warning("BOT shutting down.")
    await dp.storage.wait_closed()
    logger.warning("BOT down.")


def start_bot() -> None:
    """Инициализация и старт бота"""

    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )


if __name__ == '__main__':
    start_bot()
