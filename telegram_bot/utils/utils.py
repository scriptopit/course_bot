import datetime

from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message
from keyboards.keyboards import AdminButton


async def write_to_storage(state, url, packet, tag) -> None:
    """ Открывает storage пользователя и записывает туда ссылку """

    async with state.proxy() as data:
        data["url"] = url
        data["packet"] = packet
        data["tag"] = tag


async def collect_data_and_send(data: list, message: Message) -> None:
    """ Принимаем список объектов валидатора, возвращаем строку с данными """

    text = "telegram_id | username | tag | expired_at\n\n"

    for user in data:
        # datetime_object = datetime.datetime.strptime(
        #     user.expired_at, '%Y-%m-%dT%H:%M:%S%z').replace(
        #     microsecond=0
        # )
        datetime_object = datetime.datetime.fromisoformat(
            user.expired_at).replace(microsecond=0)

        text += f"{user.telegram_id} - " \
                f"{user.username} - " \
                f"{'FREE' if not user.tag else user.tag} - " \
                f"{str(datetime_object)[:-6]}\n"

        if len(text) >= 3900:
            await message.answer(
                text=text
            )
            text = f""

    if len(text) > 0:
        await message.answer(
            text=text,
            reply_markup=AdminButton.keyboard()
        )


async def developer_photo():
    """ Open a photo for menu 'about developer' and return """

    photo = open('img/img.png', 'rb')
    return photo
