from telegram_bot.config import bot, Dispatcher
from aiogram.types import Message
from telegram_bot.keyboards.keyboards import StartMenu


async def main_menu(message: Message) -> None:
    await message.answer(
        text=f"Главное меню",
        reply_markup=StartMenu.keyboard()
    )


def register_main_handlers(dp: Dispatcher) -> None:
    """ Регистрирует MAIN хэндлеры приложения """

    dp.register_message_handler(
        main_menu, commands=["start"], state=None)