from config import bot, Dispatcher
from aiogram.types import Message
from keyboards.keyboards import StartMenu, SubsMenu, PayButton
from aiogram.dispatcher.filters import Text
from states.states import SubscriptionState
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from classes.api_requests import UserAPI
from messages.main_message import *


async def main_menu(message: Message) -> None:
    await UserAPI.create_user(
        telegram_id=message.from_user.id, nick_name=message.from_user.username)

    await message.answer(
        text=f"Главное меню",
        reply_markup=StartMenu.keyboard()
    )


async def buy_subscription(message: Message, state: FSMContext) -> None:
    """ Хэндлер для покупки подписки """

    async with state.proxy() as data:
        data["telegram_id"] = message.from_user.id
        data["username"] = message.from_user.username

    for text in (sub_text, base_packet, pro_packet, vip_packet):
        await message.answer(
            text=text,
            reply_markup=SubsMenu.keyboard(),
            parse_mode="Markdown"
        )
    await SubscriptionState.choose_sub_packet.set()


async def choose_sub_packet(message: Message, state: FSMContext) -> None:
    """ Хэндлер на название тарифа для оплаты подписки """

    async with state.proxy() as data:
        data["packet"] = message.text

    if message.text == SubsMenu.base_packet:

        link = await UserAPI.buy_subscription(
            packet="base", telegram_id=message.from_user.id, username=message.from_user.username)
        if link:
            await message.answer(
                text=base_packet_price_menu,
                parse_mode="Markdown",
                reply_markup=PayButton.keyboard(url=link)
            )

    elif message.text == SubsMenu.pro_packet:
        link = await UserAPI.buy_subscription(
            packet="pro", telegram_id=message.from_user.id, username=message.from_user.username)

        await message.answer(
            text=pro_packet_price_menu,
            parse_mode="Markdown",
            reply_markup=PayButton.keyboard(url=link)
        )
    elif message.text == SubsMenu.vip_packet:
        link = await UserAPI.buy_subscription(
            packet="vip", telegram_id=message.from_user.id, username=message.from_user.username)

        await message.answer(
            text=vip_packet_price_menu,
            parse_mode="Markdown",
            reply_markup=PayButton.keyboard(url=link)
        )
    else:
        await message.answer(
            text=f"Вы выбрали неизвестный тариф.\n"
                 f"Что-то пошло не так, попробуйте еще раз",
            reply_markup=StartMenu.keyboard(),
            parse_mode="Markdown"
        )
        await state.finish()


def register_main_handlers(dp: Dispatcher) -> None:
    """ Регистрирует MAIN хэндлеры приложения """

    dp.register_message_handler(
        main_menu, commands=["start"], state=None)
    dp.register_message_handler(
        buy_subscription, Text(equals=StartMenu.buy_subscription))
    dp.register_message_handler(
        choose_sub_packet, Text(contains="Python"), state=SubscriptionState.choose_sub_packet)
