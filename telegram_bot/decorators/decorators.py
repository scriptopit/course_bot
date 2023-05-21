from aiogram import types
from config import logger, settings
from typing import Union, Callable, Awaitable, Optional


def admin_only(func: Callable[..., Awaitable[None]]) -> Optional[Callable[..., Awaitable[None]]]:
    async def wrapper(message: types.Message) -> None:

        if message.from_user.id in settings.ADMINS:
            await func(message)
        else:
            logger.error("Access denied for non-admin user: %s", message.from_user.id)

    return wrapper
