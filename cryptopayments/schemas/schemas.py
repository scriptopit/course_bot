from pydantic import BaseModel
from models.models import User

from tortoise.contrib.pydantic import \
    pydantic_model_creator


class UserCreate(BaseModel):
    telegram_id: int
    username: str


class UserTelegramId(BaseModel):
    telegram_id: int = 0


class SubscriptionUser(UserCreate):
    packet: str
    price: int


class AddChanel(BaseModel):
    channel_id: int
    tag: str


class AddPacket(BaseModel):
    subscribe: str
    price: int
    channel: int


class UserActivityChange(UserTelegramId):
    tag: str


class GetChannelId(BaseModel):
    tag: str


UserPydantic = pydantic_model_creator(User, exclude=('invoice_id',))
