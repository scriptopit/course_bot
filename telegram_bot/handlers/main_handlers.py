from config import bot, Dispatcher
from aiogram.types import Message
from keyboards.keyboards import StartMenu
from aiogram.dispatcher.filters import Text
from messages.main_message import *


async def main_menu(message: Message) -> None:
    await message.answer(
        text=f"Главное меню",
        reply_markup=StartMenu.keyboard()
    )


async def buy_subscription(message: Message) -> None:
    """ Хэндлер для покупки подписки """

    for text in (sub_text, base_packet, pro_packet, vip_packet):
        await message.answer(
            text=text,
            reply_markup=StartMenu.keyboard(),
            parse_mode="Markdown"
        )


def register_main_handlers(dp: Dispatcher) -> None:
    """ Регистрирует MAIN хэндлеры приложения """

    dp.register_message_handler(
        main_menu, commands=["start"], state=None)
    dp.register_message_handler(
        buy_subscription, Text(equals=StartMenu.buy_subscription))
