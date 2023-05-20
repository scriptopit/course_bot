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
