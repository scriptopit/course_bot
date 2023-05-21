from config import bot, Dispatcher, settings
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from config import bot, Dispatcher
from keyboards.keyboards import AdminButton, BaseMenu, YesOrNo, ChatTags
from states.states import AdminState
from classes.api_requests import AdminAPI


async def admin_menu(message: Message) -> None:
    """ Главное меню админ-панели """

    await message.answer(
        text=f"Админ меню:",
        reply_markup=AdminButton.keyboard()
    )


async def add_channel(message: Message) -> None:
    """ Хэндлер на добавление нового канала в базу данных """

    await AdminState.add_new_channel.set()
    await message.answer(
        text=f"Перешлите сообщение из канала который хотите добавить",
        reply_markup=BaseMenu.keyboard()
    )


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


async def validate_data(message: Message, state: FSMContext) -> None:
    """ Получает подтверждение или отказ от пользователя и выполняет запрос """

    data = await state.get_data()

    if message.text == YesOrNo.yes_button:
        await AdminAPI.add_channel(
            channel_id=data['channel_id'],
            tag=data['tag']
        )
    else:
        await message.answer(
            text=f"Тогда попробуйте заново",
            reply_markup=AdminButton.keyboard()
        )
        await state.finish()


async def user_free_sub(message: Message) -> None:
    """ Добавляет пользователя в базу данных мимо кассы """

    await message.answer(
        text=f"Перешлите сообщение от пользователя которого хотите внести в БД",
        reply_markup=BaseMenu.keyboard()
    )
    await AdminState.get_user_info.set()


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
            text=f"Идентификатор пользователя {message.from_user.last_name}:"
                 f" {message.from_user.id}."
                 f"Теперь выберите пакет обучения который хотите ему выдать"
        )
        async with state.proxy() as data:
            data['user_id'] = message.from_user.id
            data['username'] = message.from_user.username

        await AdminState.choose_tag_user.set()


async def accumulate_data_and_send(message: Message, state: FSMContext) -> None:
    """ Собирает данные для выдачи бесплатной подписки и добавляет пользователя в БД """

    if message.text in list(ChatTags.__dict__.values()):
        await message.answer(
            text=f"Получен тэг: {message.text}\n"
                 f"Записываю в базу данных нового ученика",
            reply_markup=AdminButton.keyboard()
        )
        data = await state.get_data()
        await AdminAPI.activate_user(telegram_id=data['telegram_id'], tag=message.text)

    else:
        await message.answer(
            text=f"Вы ввели неизвестный тэг: {message.text}\n"
                 f"Попробуйте заново",
            reply_markup=AdminButton.keyboard()
        )
    await state.finish()


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
        )

