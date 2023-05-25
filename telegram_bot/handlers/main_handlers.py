import datetime
import time
import loguru

from config import bot, Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.keyboards import StartMenu, SubsMenu, PayButton, UrlButton
from aiogram.dispatcher.filters import Text
from states.states import SubscriptionState
from aiogram.dispatcher.storage import FSMContext
from classes.api_requests import UserAPI
from utils.utils import write_to_storage, developer_photo
from api.utils_schemas import DataStructure
from messages.main_message import *
from aiogram.utils.callback_data import CallbackData


async def main_menu(message: Message) -> None:
    await UserAPI.create_user(
        telegram_id=message.from_user.id, nick_name=message.from_user.username)

    await message.answer(
        text=f"Главное меню",
        reply_markup=StartMenu.keyboard()
    )


async def buy_subscription_packet(message: Message, state: FSMContext) -> None:
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
        data["telegram_id"] = message.from_user.id
        data["tag"] = message.text.split(" ")[-1].lower()

    if message.text == SubsMenu.base_packet:

        link = await UserAPI.buy_subscription(
            packet="base", telegram_id=message.from_user.id,
            username=message.from_user.username, price=1)
        await write_to_storage(
            state=state, url=link, packet=base_packet_price_menu, tag="base")

        if link:
            await message.answer(
                text=base_packet_price_menu,
                parse_mode="Markdown",
                reply_markup=PayButton.keyboard(url=link)
            )

    elif message.text == SubsMenu.pro_packet:
        link = await UserAPI.buy_subscription(
            packet="pro", telegram_id=message.from_user.id,
            username=message.from_user.username, price=179)
        await write_to_storage(
            state=state, url=link, packet=pro_packet_price_menu, tag="pro")

        await message.answer(
            text=pro_packet_price_menu,
            parse_mode="Markdown",
            reply_markup=PayButton.keyboard(url=link)
        )
    elif message.text == SubsMenu.vip_packet:
        link = await UserAPI.buy_subscription(
            packet="vip", telegram_id=message.from_user.id,
            username=message.from_user.username, price=269)
        await write_to_storage(
            state=state, url=link, packet=vip_packet_price_menu, tag="vip")

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


async def payment_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """ Ловит callback check_payment и отвечает на него """

    if callback.data == "check_payment":

        await callback.message.delete()
        data = await state.get_data()
        message_data: Message = await callback.message.answer(
            "⌛ Получаю информацию по статусу вашего инвойса...",
            reply_markup=ReplyKeyboardRemove())
        telegram_id: int = int(callback.from_user.id)
        loguru.logger.info(f"Во время проверки: {telegram_id}")
        subscribe_data: DataStructure = await UserAPI.check_payment(
            telegram_id=telegram_id, tag=data["tag"])

        if not subscribe_data:
            await callback.message.answer(
                "Ошибка запроса к базе данных при получении информации для подписки.",
                reply_markup=StartMenu.keyboard())
            await state.finish()
            return

        await message_data.delete()

        if subscribe_data.status != 200:
            await callback.message.answer(
                text=data["packet"],
                reply_markup=PayButton.keyboard(url=data['url']),
                parse_mode="Markdown"
            )
        else:
            chat_id = await UserAPI.get_id_channel(tag=data['tag'])

            url = await bot.create_chat_invite_link(
                chat_id=chat_id.message,
                expire_date=datetime.datetime.now().replace(
                    microsecond=0) + datetime.timedelta(hours=12),
                member_limit=1
            )

            await callback.message.answer(
                text=f"🎁 Вы успешно приобрели подписку, "
                     f"вот ваша личная ссылка для подключения к каналу с ментором.\n",
                reply_markup=UrlButton.keyboard(url=url.invite_link)
            )
            await state.finish()

    elif callback.data == "cancel":

        await state.finish()
        await callback.message.delete()
        await callback.message.answer(
            text=f"Успешная отмена",
            reply_markup=StartMenu.keyboard()
        )

    await callback.answer()


async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    await message.reply(
        text=f"Успешная отмена", reply_markup=StartMenu.keyboard())
    if current_state is None:
        return
    await state.finish()


async def callback_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    """ Отвечает на CALLBACK кнопки CANCEL """

    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()

    await callback.message.answer(
        text=f"Успешная отмена",
        reply_markup=StartMenu.keyboard()
    )

    await callback.answer()


async def info_about(message: Message) -> None:
    """ Возвращает информацию про администрацию ментор-сервиса """

    await bot.send_photo(
        photo=await developer_photo(),
        caption='📇 Instagram: [iTDeal Group](https://www.instagram.com/itdealgroup/)'
                '\n👨‍💻 Telegram Channel: [Pythonic Bytes](t.me/pybytes)'
                '\n👨‍💻 Telegram Chat: [PyBytes Chat](t.me/pybytes_chat)'
                '\n👨‍💻 Telegram: [A B BOT ](t.me/lunasantrope)',
        chat_id=message.from_user.id,
        parse_mode='Markdown',
        reply_markup=StartMenu.keyboard()
    )


def register_main_handlers(dp: Dispatcher) -> None:
    """ Регистрирует MAIN хэндлеры приложения """

    dp.register_message_handler(
        main_menu, commands=["start"], state=None)
    dp.register_message_handler(
        buy_subscription_packet, Text(equals=StartMenu.buy_subscription))
    dp.register_message_handler(
        choose_sub_packet, Text(contains="Python"), state=SubscriptionState.choose_sub_packet)
    dp.register_callback_query_handler(
        payment_callback, state=SubscriptionState.choose_sub_packet)
    dp.register_message_handler(
        info_about, Text(equals=StartMenu.information), state=None)
    dp.register_message_handler(
        cancel_handler, Text(equals="Отмена" or "отмена"), state=["*"])

