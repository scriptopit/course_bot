import datetime
import time
import loguru

from config import bot, Dispatcher, HELPERS_CHAT
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.keyboards import StartMenu, SubsMenu, \
    PayButton, UrlButton, YesOrNo, BaseMenu, StudentButtons
from aiogram.dispatcher.filters import Text
from states.states import SubscriptionState, TicketStates
from aiogram.dispatcher.storage import FSMContext
from classes.api_requests import UserAPI, AdminAPI
from utils.utils import write_to_storage, developer_photo
from api.utils_schemas import DataStructure
from messages.main_message import *
from decorators.decorators import private_message


@private_message
async def main_menu(message: Message) -> None:
    await UserAPI.create_user(
        telegram_id=message.from_user.id, nick_name=message.from_user.username)

    await message.answer(
        text=f"Главное меню",
        reply_markup=StartMenu.keyboard()
    )

@private_message
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


@private_message
async def choose_sub_packet(message: Message, state: FSMContext) -> None:
    """ Хэндлер на название тарифа для оплаты подписки """

    async with state.proxy() as data:
        data["packet"] = message.text
        data["telegram_id"] = message.from_user.id
        data["tag"] = message.text.split(" ")[-1].lower()

    if message.text == SubsMenu.base_packet:

        link = await UserAPI.buy_subscription(
            packet="base", telegram_id=message.from_user.id,
            username=message.from_user.username, price=99)
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


@private_message
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    await message.reply(
        text=f"Успешная отмена", reply_markup=StartMenu.keyboard())
    if current_state is None:
        return
    await state.finish()


@private_message
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


@private_message
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


@private_message
async def support_menu(message: Message) -> None:
    """ Хэндлер для ответа на кнопку 'поддержка' """

    await message.answer(
        text=f'Вы желаете создать тиккет в службу поддержки?',
        reply_markup=YesOrNo.keyboard()
    )

    await TicketStates.open_ticket.set()


@private_message
async def ticket_create_helper(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает нажатие на кнопку для создание тиккета в стэйте
    """

    if message.text == YesOrNo.yes_button:
        await message.answer(
            text=f"💡 Опишите суть вашей проблемы либо вопрос.\n"
                 f"💼 Наши хелперы свяжутся с вами и вы получите ответ в ближайшее время.\n"
                 f""
                 f"\nЕсли вы передумали - нажмите кнопку \"Отмена\"",
            reply_markup=BaseMenu.keyboard()
        )

        await TicketStates.input_ticket_info.set()

    else:
        await state.finish()
        await message.answer(
            text=f"Главное меню",
            reply_markup=StartMenu.keyboard()
        )


@private_message
async def get_ticket_data_from_user(message: Message, state: FSMContext) -> None:
    """
    Забирает сообщение тикета у пользователя и проходит дополнительную проверку на правильность введенного запроса
    """

    if len(message.text) < 3500:

        async with state.proxy() as data:
            data["username"] = message.from_user.username
            data["first_name"] = message.from_user.first_name
            data["last_name"] = message.from_user.last_name
            data["created_at"] = datetime.datetime.now().replace(microsecond=0)
            data["text"] = message.text
            data["user_id"] = message.from_user.id

            await message.answer(
                text=f"Тикет успешно создан, "
                     f"проверьте правильность введенных данных\n"
                     f"\nВаш username: {message.from_user.username}"
                     f"\nВаше имя: {message.from_user.first_name} "
                     f"{'' if data['last_name'] is None else data['last_name']}"
                     f"\nДата создания: {datetime.datetime.now().replace(microsecond=0)}"
                     f"\n\n*Текст: {message.text}*"
                     f"\n\n\n"
                     f"Отправляем тикет?",
                reply_markup=YesOrNo.keyboard(),
                parse_mode="Markdown"
            )
            await TicketStates.accept_ticket.set()
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Вы ввели текст превышающий ограничение!\n"
                 f"Максимальное кол-во символов: 3500 символов\n"
                 f"Вы ввели: {len(message.text)}",
            reply_markup=StartMenu.keyboard()
        )
        await state.finish()


@private_message
async def accept_ticket_or_decline(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает колбэки при отправке или отмене создания нового тикета
    """

    if message.text == YesOrNo.yes_button:
        async with state.proxy() as data:

            text = f"📌 НОВЫЙ ТИКЕТ 📌\n\n" \
                   f"ID: | {data['user_id']} | \n" \
                   f"Username: {data['username']}" \
                   f"\nИмя: {data['first_name']}\n" \
                   f"Фамилия: {data['last_name']}\n" \
                   f"Дата создания: {data['created_at']}\n" \
                   f"\n\n" \
                   f"{data['text']}"

            if len(text) > 4096:
                for x in range(0, len(text), 4096):
                    await bot.send_message(chat_id=int(HELPERS_CHAT), text=text[x:x + 4096])
            else:
                await bot.send_message(chat_id=int(HELPERS_CHAT), text=text)

            await bot.send_message(
                chat_id=message.from_user.id,
                text=f"Ваш тикет успешно отправлен.\n"
                     f"Вы получите ответ в течении ближайшего времени, ожидайте ответа хелпера",
                reply_markup=StartMenu.keyboard()
            )

    else:
        await message.answer(
            text=f"Главное меню",
            reply_markup=StartMenu.keyboard()
        )
    await state.finish()


@private_message
async def knowledge_menu(message: Message) -> None:
    """ Меню ученика с активной подпиской """

    user_models = await AdminAPI.get_active_users()
    clear_users = [user.telegram_id for user in user_models]

    if message.from_user.id in clear_users:
        await message.answer(
            text=f"Перед вами меню образовательного портала",
            reply_markup=StudentButtons.keyboard()
        )
    else:
        await message.answer(
            text=f"🐍 Это меню доступно только для учеников сервиса\n"
                 f"🐍 Для начала необходимо приобрести подписку!",
            reply_markup=StartMenu.keyboard()
        )


@private_message
async def my_academy_stats(message: Message) -> None:
    """ Выводит пользователю статистику по его обучению """

    module_id = await UserAPI.get_module_id(telegram_id=message.from_user.id)

    await message.answer(
        text=f"🎩 На данный момент вы проходите {module_id} из 30 модулей\n"
             f"💡 Дипломная работа: Не сдана",
        reply_markup=StudentButtons.keyboard()
    )


@private_message
async def homework_menu(message: Message) -> None:
    """ Меню сдачи домашней работы """

    await message.answer(
        text=f"COMING SOON\n\n"
             f"Сдавай в личные сообщения своему куратору!",
        reply_markup=StudentButtons.keyboard()
    )


@private_message
async def get_next_lesson(message: Message) -> None:
    """ Отрабатывает для выдачи пользователю нового учебного материала """

    links = await UserAPI.get_current_module(telegram_id=message.from_user.id)

    if links:
        await message.answer(
            text=f"🐍 Вот следующий материал для изучения\n"
                 f"По готовности сдайте домашнее задание своему куратору\n\n"
                 f"{links}",
            reply_markup=StudentButtons.keyboard()
        )
    else:
        await message.answer(
            text=f"🐍 Вы еще не начали учиться в нашей академии, сначала выберите тариф",
            reply_markup=StartMenu.keyboard()
        )

#
# async def del_keyboard(message: Message):
#     await message.reply(
#         text=f"Удалена клавиатура",
#         reply_markup=ReplyKeyboardRemove()
#     )


def register_main_handlers(dp: Dispatcher) -> None:
    """ Регистрирует MAIN хэндлеры приложения """

    # dp.register_message_handler(
    #     del_keyboard, commands=['/del'])
    dp.register_message_handler(
        cancel_handler, Text(equals="Отмена" or "отмена"), state=["*"])
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
        support_menu, Text(equals=StartMenu.support), state=None)
    dp.register_message_handler(
        ticket_create_helper, state=TicketStates.open_ticket)
    dp.register_message_handler(
        get_ticket_data_from_user, state=TicketStates.input_ticket_info)
    dp.register_message_handler(
        accept_ticket_or_decline, state=TicketStates.accept_ticket)
    dp.register_message_handler(
        knowledge_menu, Text(equals=StartMenu.student_menu))
    dp.register_message_handler(
        my_academy_stats, Text(equals=StudentButtons.my_academy))
    dp.register_message_handler(
        homework_menu, Text(equals=StudentButtons.submit_homework))
    dp.register_message_handler(
        get_next_lesson, Text(equals=StudentButtons.next_module))

