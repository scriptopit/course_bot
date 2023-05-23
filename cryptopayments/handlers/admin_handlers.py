import datetime

from fastapi import APIRouter, Request

from services.utils import check_token
from models.models import User, \
    Statuses, Group
from schemas.schemas import UserTelegramId, UserPydantic,\
    AddChanel, AddPacket, UserActivityChange
from typing import Any
from services import exceptions


admin_router = APIRouter()


@admin_router.get("/get_user_list", response_model=list[UserPydantic], tags=['admin'])
async def get_user_list(request: Request) -> list:
    await check_token(request)

    return await User.all()


@admin_router.post("/get_user_status", tags=['admin'])
async def get_user_status(data: UserTelegramId, request: Request) -> dict:
    await check_token(request)

    user = await User.get(telegram_id=data.telegram_id)
    if user:
        return {"status": user.status}


@admin_router.post("/deactivate_user", tags=['admin'])
async def deactivate_user(data: UserTelegramId, request: Request) -> dict:
    await check_token(request)
    result = await User.filter(telegram_id=data.telegram_id).update(
        status=Statuses.dead_enemy,
        expired_at=datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(minutes=5),
        tag=""
    )
    return {"result": result}


@admin_router.post("/activate_user", tags=['admin'])
async def activate_user(data: UserActivityChange, request: Request) -> dict:
    await check_token(request)
    result = await User.filter(telegram_id=data.telegram_id).update(
        tag=data.tag,
        status=Statuses.member,
        expired_at=datetime.datetime.now().replace(microsecond=0)
    )
    return {"result": result}


@admin_router.get("/get_active_users", response_model=list[UserTelegramId], tags=['admin'])
async def get_active_users(request: Request) -> list:
    await check_token(request)

    return await User.filter(status=Statuses.member)


@admin_router.post("/add_channel", tags=['admin'])
async def add_channel(channel: AddChanel, request: Request) -> dict[str, Any]:
    await check_token(request)
    check = await Group.get_or_none(channel_id=channel.channel_id)

    if not check:
        group_create: dict = {
            "tag": channel.tag,
            "channel_id": channel.channel_id
        }
        response = await Group.create(**group_create)
        return response
    else:
        raise exceptions.ChannelExistsException

