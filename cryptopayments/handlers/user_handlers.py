import datetime

from starlette import status
from fastapi import APIRouter, Request, Response

from cryptopayments.services.utils import check_token
from cryptopayments.schemas.data_schemas import DataStructure
from cryptopayments.schemas.schemas import UserCreate
from cryptopayments.models.models import User
from cryptopayments.services.exceptions import UserExistsException

user_router = APIRouter()


@user_router.post("/create_user", response_model=DataStructure, tags=['user'])
async def create_user(user: UserCreate, response: Response, request: Request):
    await check_token(request)
    result = DataStructure()
    if await User.exists(telegram_id=user.telegram_id):
        raise UserExistsException
    user_data = {
        'username': user.username,
        'telegram_id': user.telegram_id,
        'expired_at': datetime.datetime.now()
    }
    await User.create(**user_data)
    result.status = 200
    result.success = True
    result.data = {}
    response.status_code = status.HTTP_201_CREATED
    return result.as_dict()
