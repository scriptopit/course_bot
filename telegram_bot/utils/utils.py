from aiogram.dispatcher.storage import FSMContext


async def write_to_storage(state, url, packet, tag) -> None:
    """ Открывает storage пользователя и записывает туда ссылку """

    async with state.proxy() as data:
        data["url"] = url
        data["packet"] = packet
        data["tag"] = tag
