import datetime
import logging

import loguru
from starlette import status
from fastapi import APIRouter, Request, Response

from services.utils import check_token, create_invoice, get_invoice_status
from schemas.data_schemas import DataStructure
from models.models import User, Statuses, Group
from services import exceptions
from schemas.schemas import UserCreate,\
    SubscriptionUser, UserTelegramId, GetChannelId

user_router = APIRouter()


@user_router.post("/create_user", response_model=DataStructure, tags=['user'])
async def create_user(user: UserCreate, response: Response, request: Request):
    await check_token(request)
    result = DataStructure()
    if await User.exists(telegram_id=user.telegram_id):
        raise exceptions.UserExistsException
    user_data = {
        'username': user.username,
        'telegram_id': user.telegram_id,
    }
    await User.create(**user_data)

    result.status = 200
    result.success = True
    result.data = ""
    response.status_code = status.HTTP_201_CREATED
    return result.as_dict()


@user_router.post("/buy_subscription", response_model=DataStructure, tags=['user'])
async def buy_subscription(subscription: SubscriptionUser, response: Response, request: Request):
    await check_token(request)

    result = DataStructure()
    invoice = await create_invoice(amount=subscription.price)

    await User.filter(telegram_id=subscription.telegram_id).update(
        invoice_id=invoice.invoice_id)

    result.status = 200
    result.success = True
    result.message = invoice.pay_url
    response.status_code = status.HTTP_200_OK
    return result.as_dict()


@user_router.post("/check_payment", response_model=DataStructure, tags=['user'])
async def check_payment(user: UserTelegramId, response: Response, request: Request):
    await check_token(request)

    result = DataStructure()
    invoice_id = await User.get_or_none(telegram_id=user.telegram_id)
    loguru.logger.info(f"INVOICE STATUS: {invoice_id} . {user.telegram_id}")
    if invoice_id:
        check = await get_invoice_status(invoice_id=invoice_id.invoice_id)
        if check:
            await User.filter(telegram_id=user.telegram_id).update(
                status=Statuses.member,
                expired_at=datetime.datetime.utcnow()
            )

            result.status = 200
            result.success = True
            response.status_code = status.HTTP_200_OK
            return result.as_dict()

    response.status_code = status.HTTP_402_PAYMENT_REQUIRED
    result.status = 402
    result.success = True
    return result


@user_router.post("/get_id_channel", response_model=DataStructure, tags=['user'])
async def get_id_channel(data: GetChannelId, request: Request):
    await check_token(request)
    result = DataStructure()

    chat_id = await Group.get_or_none(tag=data.tag)

    if chat_id:
        result.status = 200
        result.success = True
        result.message = str(chat_id.channel_id)
        return result.as_dict()

    result.status = 400
    result.success = True
    return result.as_dict()



