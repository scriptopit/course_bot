from dataclasses import dataclass
from typing import Union

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import logger


def default_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        row_width=3
    )


@dataclass(frozen=True)
class BaseMenu:
    cancel_key: str = "Отмена"

    @classmethod
    @logger.catch
    def _keyboard(cls) -> Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]:
        """ Возвращает кнопку Отмена """

        return default_keyboard().add(KeyboardButton(cls.cancel_key))


@dataclass(frozen=True)
class StartMenu(BaseMenu):
    """ Стандартное меню пользователя """

    buy_subscription: str = "Купить подписку"
    support: str = "Поддержка"
    information: str = "Информация"

    @classmethod
    @logger.catch
    def keyboard(cls) -> 'ReplyKeyboardMarkup':
        """ Возвращает кнопочки меню для канала из списка """

        return default_keyboard().add(
            KeyboardButton(cls.buy_subscription),
            KeyboardButton(cls.support),
            KeyboardButton(cls.information)
        )











