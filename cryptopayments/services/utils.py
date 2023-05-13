import asyncio

from fastapi import Request

from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.models.invoice import PaidButtons
from cryptopayments.config import settings, logger, crypto
from exceptions import exception_unauthorized


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
        paid_btn_url="https://t.me/pybytes",
        expires_in=18000,
        hidden_message="🎁 Поздравляем с приобретением курса, "
                       "надеемся что твой путь будет легкий и полный удач."
                       "\nТвоим куратором будет @python_devss"
    )

    return invoice


async def get_invoice_status(invoice_id: int) -> bool:
    """ Проверяет номер инвойса и возвращает булево значение """

    check = await crypto.get_invoices(invoice_ids=invoice_id)
    status = check.status

    if status == "paid":
        return True
    return False
