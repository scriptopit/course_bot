import loguru
import datetime

from config import bot, Dispatcher, settings
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from states.states import AdminState
from classes.api_requests import AdminAPI, UserAPI
from decorators.decorators import check_super_admin
from utils.utils import collect_data_and_send
from keyboards.keyboards import AdminButton, BaseMenu, \
    YesOrNo, ChatTags, UrlButton, StartMenu


@check_super_admin
async def admin_menu(message: Message) -> None:
    """ Главное меню админ-панели """

    await message.answer(
        text=f"Админ меню:",
        reply_markup=AdminButton.keyboard()
    )


@check_super_admin
async def add_channel(message: Message) -> None:
    """ Хэндлер на добавление нового канала в базу данных """

    await AdminState.add_new_channel.set()
    await message.answer(
        text=f"Перешлите сообщение из канала который хотите добавить",
        reply_markup=BaseMenu.keyboard()
    )


@check_super_admin
async def get_channel_data(message: Message, state: FSMContext) -> None:
    """ Получает про канал информацию и отправляет в базу данных """

    await AdminState.processing.set()
    channel_id: int = message.forward_from_chat.id

    async with state.proxy() as data:
        data["channel_id"] = channel_id

    await message.answer(
        text=f"Получен chat_id: {channel_id}\n"
             f"Верно?",
        reply_markup=YesOrNo.keyboard()
    )


@check_super_admin
async def response_processing(message: Message, state: FSMContext) -> None:
    """ Проверяет ответ пользователя и выполняет определенные события """

    if message.text == YesOrNo.yes_button:
        await message.answer(
            text=f"Выберите тэг чата",
            reply_markup=ChatTags.keyboard()
        )
        await AdminState.receive_tag.set()

    else:
        await message.answer(
            text=f"Тогда попробуйте заново",
            reply_markup=AdminButton.keyboard()
        )
        await state.finish()


@check_super_admin
async def insert_chat_tag(message: Message, state: FSMContext) -> None:
    """ Получает от пользователя введенный тэг который будет являться названием канала """

    async with state.proxy() as data:
        data['tag'] = message.text

        await message.answer(
            text=f"Вы ввели данные:\n"
                 f"chat_id: {data['channel_id']}\n"
                 f"tag: {data['tag']}\n\n"
                 f"Верно?",
            reply_markup=YesOrNo.keyboard()
        )

        await AdminState.check_data.set()


@check_super_admin
async def validate_data(message: Message, state: FSMContext) -> None:
    """ Получает подтверждение или отказ от пользователя и выполняет запрос """

    data = await state.get_data()

    if message.text == YesOrNo.yes_button:
        response = await AdminAPI.add_channel(
            channel_id=data['channel_id'],
            tag=data['tag']
        )

        if response.status == 409:
            text: str = "Канал уже добавлен в какой то из тарифов.\n" \
                           "Открепите его для начала"
        elif response.status == 200:
            text: str = f"Канал {data['channel_id']} успешно добавлен в тариф {data['tag'].upper()}"
        else:
            text = response

        await message.answer(
            text=text,
            reply_markup=AdminButton.keyboard()
        )

    else:
        await message.answer(
            text=f"Тогда попробуйте заново",
            reply_markup=AdminButton.keyboard()
        )
    await state.finish()


@check_super_admin
async def user_free_sub(message: Message) -> None:
    """ Добавляет пользователя в базу данных мимо кассы """

    await message.answer(
        text=f"Перешлите сообщение от пользователя которого хотите внести в БД",
        reply_markup=BaseMenu.keyboard()
    )
    await AdminState.get_user_info.set()


@check_super_admin
async def info_user_filter(message: Message, state: FSMContext) -> None:
    """ Получает ID пользователя и добавляет его в базу данных """

    if not message.forward_from:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'Попросите пользователя в настройках '
                 f'конфиденциальности изменить параметр '
                 f'"Пересылка сообщений" на "Все", и попробуйте еще раз',
            reply_markup=BaseMenu.keyboard()
        )

    else:
        await message.answer(
            reply_markup=ChatTags.keyboard(),
            text=f"Идентификатор пользователя {message.forward_from.first_name}:"
                 f" {message.forward_from.id}.\n"
                 f"Теперь выберите пакет обучения который хотите ему выдать"
        )
        async with state.proxy() as data:
            data['user_id'] = message.forward_from.id
            data['username'] = message.forward_from.username

        await AdminState.choose_tag_user.set()


@check_super_admin
async def accumulate_data_and_send(message: Message, state: FSMContext) -> None:
    """ Собирает данные для выдачи бесплатной подписки и добавляет пользователя в БД """

    if message.text in list(ChatTags.__dict__.values()):
        await message.answer(
            text=f"Получен тэг: {message.text}\n"
                 f"Записываю в базу данных нового ученика",
            reply_markup=AdminButton.keyboard()
        )

        data = await state.get_data()
        response = await AdminAPI.activate_user(telegram_id=data['user_id'], tag=message.text)

        if response["status"] == 200:
            chat_id = await UserAPI.get_id_channel(tag=message.text)

            url = await bot.create_chat_invite_link(
                chat_id=str(chat_id.message),
                expire_date=datetime.datetime.now().replace(
                    microsecond=0) + datetime.timedelta(hours=12),
                member_limit=1
            )

            await bot.send_message(
                text=f"🎁 Вам выдали доступ к тарифу {message.text.upper()}\n"
                     f"Желаем приятного обучения!",
                chat_id=data['user_id'],
                reply_markup=UrlButton.keyboard(url=url.invite_link)
            )

        else:
            await message.answer(
                text=f"Пользователя нет в базе данных, он должен прописать /start",
                reply_markup=AdminButton.keyboard()
            )

    else:
        await message.answer(
            text=f"Вы ввели неизвестный тэг: {message.text}\n"
                 f"Попробуйте заново",
            reply_markup=AdminButton.keyboard()
        )
    await state.finish()


@check_super_admin
async def deactivate_user_handle(message: Message) -> None:
    """ Активирует хэндлер на деактивацию пользователя и ставит в стэйт """

    await message.answer(
        text=f"Перешлите сообщение от пользователя которого хотите внести в БД",
        reply_markup=BaseMenu.keyboard()
    )
    await AdminState.deactivate_user.set()


@check_super_admin
async def deactivate_sub(message: Message, state: FSMContext):
    """ Запрашивает информацию о пользователе для деактивации """

    if not message.forward_from:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'Попросите пользователя в настройках '
                 f'конфиденциальности изменить параметр '
                 f'"Пересылка сообщений" на "Все", и попробуйте еще раз',
            reply_markup=BaseMenu.keyboard()
        )

    else:
        await message.answer(
            reply_markup=AdminButton.keyboard(),
            text=f"Идентификатор пользователя {message.from_user.last_name}:"
                 f" {message.from_user.id}.\n"
                 f"Сейчас он будет деактивирован!",
        )

        response = await AdminAPI.deactivate_user(telegram_id=message.from_user.id)

        if response["status"] == 200:
            await message.answer(
                text=f"Пользователь {message.from_user.id} успешно деактивирован\n"
                     f"Он будет удален с канала в ближайшие 10 минут",
                reply_markup=AdminButton.keyboard()
            )
        else:
            await message.answer(
                text=f"Пользователя нет в базе данных, для начала он должен нажать /start"
            )
        await state.finish()


@check_super_admin
async def get_active_users_handler(message: Message) -> None:
    """ Реагирует на кнопку 'Активные пользователи' """

    result = await AdminAPI.get_active_users()
    if result:
        loguru.logger.info(f"Пришло с DB: {result}")
        await collect_data_and_send(data=result, message=message)
    else:
        await message.answer(
            text=f"В базе данных нет активных пользователей",
            reply_markup=AdminButton.keyboard()
        )


@check_super_admin
async def get_service_users(message: Message) -> None:
    """ Реагирует на кнопку 'Все пользователи' """

    result = await AdminAPI.get_all_users()
    if result:
        await collect_data_and_send(message=message, data=result)
    else:
        await message.answer(
            text=f"В базе данных нет пользователей",
            reply_markup=AdminButton.keyboard()
        )


def register_admin_handlers(dp: Dispatcher) -> None:
    """ Регистрирует админ-хэндлеры приложения """

    dp.register_message_handler(
        admin_menu, commands=["admin"], state=None)
    dp.register_message_handler(
        add_channel, Text(equals=AdminButton.add_channel))
    dp.register_message_handler(
        get_channel_data, state=AdminState.add_new_channel)
    dp.register_message_handler(
        response_processing, state=AdminState.processing)
    dp.register_message_handler(
        insert_chat_tag, state=AdminState.receive_tag)
    dp.register_message_handler(
        validate_data, state=AdminState.check_data)
    dp.register_message_handler(
        user_free_sub, Text(equals=AdminButton.add_sub), state=None)
    dp.register_message_handler(
        info_user_filter, state=AdminState.get_user_info)
    dp.register_message_handler(
        accumulate_data_and_send, state=AdminState.choose_tag_user)
    dp.register_message_handler(
        deactivate_user_handle, Text(equals=AdminButton.take_sub), state=None)
    dp.register_message_handler(
        deactivate_sub, state=AdminState.deactivate_user)
    dp.register_message_handler(
        get_active_users_handler, Text(equals=AdminButton.active_subs))
    dp.register_message_handler(
        get_service_users, Text(equals=AdminButton.all_users))

