from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext
from config import logger, settings
from typing import Callable, Any
from functools import wraps
from aiogram import types


@logger.catch
def check_super_admin(func: Callable) -> Callable:
    """decorator for handler check user on super admin"""

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        message: Message = args[0]
        telegram_id: int = message.from_user.id
        if telegram_id in settings.ADMINS:
            logger.debug(f"{func.__qualname__} User {message.from_user.id} is superadmin.")
            return await func(*args, **kwargs)
        logger.debug(f"{func.__qualname__} User {message.from_user.id} is not superadmin.")

    return wrapper


@logger.catch
def private_message(func):
    async def wrapper(message: types.Message, state: FSMContext):
        if message.chat.type == "private":
            await func(message, FSMContext)
    return wrapper
