from dataclasses import dataclass
from typing import Union
from config import logger

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,
    InlineKeyboardButton
)


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


@dataclass(frozen=True)
class SubsMenu(BaseMenu):
    """ Меню для выбора подписок обучения """

    base_packet: str = "🎩 Python BASE"
    pro_packet: str = "🎓 Python PRO"
    vip_packet: str = "💎 Python VIP"

    @classmethod
    @logger.catch
    def keyboard(cls) -> 'ReplyKeyboardMarkup':
        """ Возвращает кнопки меню для выбора тарифа подписки """

        return default_keyboard().add(
            KeyboardButton(cls.base_packet),
            KeyboardButton(cls.pro_packet),
            KeyboardButton(cls.vip_packet)
        )


@dataclass(frozen=True)
class PayButton:
    """ Кнопка 'Оплатить подписку' для редиректа в бота Crypto Pay """

    @classmethod
    @logger.catch
    def keyboard(cls, url: str) -> 'InlineKeyboardMarkup':
        """ Возвращает кнопку с ссылкой в Crypto Pay Bot """

        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=f"💵 Оплатить подписку", url=url),
            InlineKeyboardButton(text=f"Отмена", callback_data="cancel")
        )








