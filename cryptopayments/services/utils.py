from fastapi import Request

from config import settings, logger, crypto
from services.exceptions import exception_unauthorized
import requests


async def check_token(request: Request):
    """ Проверяет валидность переданного токена аутентификации """

    token = request.headers.get('token')
    if not token == settings.DB_KEY_VALIDATION:
        logger.info(f' token: {token}')
        raise exception_unauthorized


async def create_invoice(amount: int):
    """ Создает инвойс в Crypto Bot """

    invoice = await crypto.create_invoice(
        asset="USDT",
        amount=amount,
        description="Оплата курсов Pythonic Bytes",
        paid_btn_name="openChannel",
        paid_btn_url="https://t.me/pybytes_academybot",
        expires_in=2678400,
        hidden_message="🎁 Поздравляем с приобретением курса, "
                       "надеемся что твой путь будет легкий и полный удач.\n"
                       "Тебе необходимо перейти в бота и нажать кнопку 'Проверить оплату'\n"
                       "После чего ты получишь доступ к материалу!"
    )

    return invoice


async def get_invoice_status(invoice_id: int) -> bool:
    """ Проверяет номер инвойса и возвращает булево значение """

    check = await crypto.get_invoices(invoice_ids=invoice_id)
    status = check.status

    if status == "paid":
        return True
    return False


def send_message_to_admins(text: str) -> None:
    for admin in settings.ADMINS:
        url: str = f"https://api.telegram.org/bot{settings.TELEBOT_TOKEN}/sendMessage?chat_id={admin}&text={text}"
        try:
            requests.get(url, timeout=5)
        except Exception as err:
            logger.error(f"requests error: {err}")


def send_message_to_user(telegram_id: int, message: str) -> None:
    """
    The function of sending the message with the result of the script
    """
    url: str = f"https://api.telegram.org/bot{settings.TELEBOT_TOKEN}/sendMessage?chat_id={telegram_id}&text={message}"
    try:
        requests.get(url, timeout=5)
        logger.info(f"telegram id: {telegram_id}\n message: {message}")
    except Exception as err:
        logger.error(f"telegram id: {telegram_id}\n message: {message}\n requests error: {err}")

