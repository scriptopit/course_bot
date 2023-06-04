from config import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.keyboards import StartMenu
from decorators.decorators import private_message
from classes.api_requests import AdminAPI, UserAPI
from api.utils_schemas import UserModel
from utils.utils import gen_sorted_list


@private_message
async def debug_handler(message: Message, state: FSMContext) -> None:
    """ Хэндлер отрабатывает на не зарегистрированные команды """

    user_list: list[UserModel] = await AdminAPI.get_all_users()
    sorted_user = await gen_sorted_list(user_list)
    username = message.from_user.username if message.from_user.username is not None else ""

    if message.from_user.id not in sorted_user:
        await UserAPI.create_user(telegram_id=message.from_user.id, nick_name=username)

    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()

    await message.answer(
        text=f"*Перед вами главное меню*",
        reply_markup=StartMenu.keyboard(),
        parse_mode="Markdown"
    )


def register_debug_handler(dp: Dispatcher) -> None:
    """ Регистрирует дебаг хэндлер """

    dp.register_message_handler(
        debug_handler, state=["*"])
