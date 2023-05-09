from fastapi import Request

from cryptopayments.config import settings, logger
from exceptions import exception_unauthorized


async def check_token(request: Request):
    token = request.headers.get('token')
    if not token == settings.DB_KEY_VALIDATION:
        logger.info(f' token: {token}')
        raise exception_unauthorized
