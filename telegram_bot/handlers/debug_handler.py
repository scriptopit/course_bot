from config import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.keyboards import StartMenu
from decorators.decorators import private_message


@private_message
async def debug_handler(message: Message, state: FSMContext) -> None:
    """ Хэндлер отрабатывает на не зарегистрированные команды """

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
