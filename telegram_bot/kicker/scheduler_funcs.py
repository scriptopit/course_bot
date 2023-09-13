from typing import List, Dict
import datetime
import asyncio

import aiogram.utils.exceptions
import aioschedule

from aiogram.types.chat import Chat

from classes.errors_reporter import MessageReporter
from config import bot, logger, KICK_RATE, HELP_RATE, HELPERS_CHAT
from kicker.get_channel_info import get_channel_data, get_helper_channel_data
from api.utils_schemas import UserModel

from classes.api_requests import UserAPI, AdminAPI


async def channel_kick_hackers(
        all_members: dict[int, dict], all_users: List[int], channel_id: str) -> None:
    """
    Удаляет пользователей телеграм ид которых нет в базе из канала
    :param all_members: словарь членов канала где ключ telegram id
    значение словарь с  подробной информацией
    :param all_users:  список пользователей полученных от API
    :param channel_id: id канала который бот администрирует
    :return:
    """

    channel: Chat = await bot.get_chat(channel_id)
    admins = await channel.get_administrators()
    all_users.extend([user.user.id for user in admins])
    all_members_id: list[int] = list(all_members.keys())

    list_for_kicked = [
        member for member in all_members_id
        if member not in all_users
    ]
    if not list_for_kicked:
        logger.info(f' No users to delete')
        return

    logger.info('List users for kicked received.\n Starting delete users for channel')
    count = 0

    for telegram_id in list_for_kicked:
        try:
            await bot.kick_chat_member(chat_id=channel_id, user_id=telegram_id)
            await bot.unban_chat_member(chat_id=channel_id, user_id=telegram_id, only_if_banned=True)
            count += 1
        except aiogram.utils.exceptions.BadRequest as err:
            member: dict = all_members.get(telegram_id, {'error': 'Не удалось получить данные'})
            text: str = 'Не удалось удалить пользователя:\n' + ''.join(
                [f'{key}: {value}\n'
                 for key, value in member.items()]
            )
            await MessageReporter.send_report_to_admins(text=text)
            logger.error(err)

    logger.info(
        f'Removed {count} users from the channel '
        f'\n list of telegram ids of kicked users: {list_for_kicked}')


async def kick_hackers() -> None:
    """
    Функция для сбора данных и удаления из канала пользователей не записанных в базе
     как члены клуба
    кроме администраторов канала
    """

    logger.info(f'start kick_hackers: {datetime.datetime.utcnow()}')
    channels: list = await AdminAPI.get_channels()

    if not channels:
        logger.warning('scheduler_func.kick_hackers: No channel')
        await MessageReporter.send_report_to_admins('Нет id канала, нужно добавить id канала.\n'
                                                    ' воспользуйтесь командой. \n/admin')
        return

    all_users_data: list[UserModel] = await AdminAPI.get_active_users()
    all_users: list[int] = [user.telegram_id for user in all_users_data]
    for channel_data in channels:
        chat_id = channel_data
        try:
            logger.info(f' try get_channel_data: {datetime.datetime.utcnow()}\nGet admins list')

            all_members: dict[int, dict] = await get_channel_data(str(chat_id)[4:])
            logger.info(f"users: {all_members}")
            if not all_members:
                logger.warning('no all members')
                await MessageReporter.send_report_to_admins(
                    'Не удалось получить пользователей канала, \n'
                    'проверьте что бот присутствует в канале и \n'
                    'является администратором. \n'
                    'Или сгенерируйте новую лицензионную сессию\n'
                )
                return
            await channel_kick_hackers(
                all_members=all_members, all_users=all_users, channel_id=chat_id)

        except Exception as err:
            logger.error(f' channel name : {channel_data} {err}')
    logger.info(f' stop kick hackers: {datetime.datetime.utcnow()}')


async def get_updates_ticket() -> None:
    """
    Получает апдэйты чата на новые ответы по тикетам и рассылкает пользователям ответы
    """

    logger.info(f'start get_updates_ticket: {datetime.datetime.utcnow()}')
    data = await get_helper_channel_data(HELPERS_CHAT)
    logger.info(f"В функцию get_updates_ticket получил список: {data}")
    ticket, answer = data

    if ticket and answer:
        user_id = ticket.split(" | ")[1]
        text = "🎟 Вам пришел ответ на открытый ранее вами тикет.\n\n" \
               f"📌Ответ: {answer}"

        await MessageReporter.send_message_to_user(text=text, telegram_id=user_id)


async def check_base():
    # aioschedule.every(KICK_RATE).minutes.do(kick_hackers)
    # aioschedule.every(HELP_RATE).minutes.do(get_updates_ticket)
    # aioschedule.every().day.at("9:00").do(mailing_to_members)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
