import loguru
from config import logger, BASE_API_URL
from api.request_classes import PostRequest, GetRequest
from api.utils_schemas import DataStructure
from typing import Union
from api.utils_schemas import UserModel


class API:
    __BASE_SERVER_URL: str = BASE_API_URL

    @classmethod
    @logger.catch
    async def _post_request(cls, data: dict, endpoint: str) -> 'DataStructure':
        """Отправляет запрос к АПИ, и возвращает ответ."""

        logger.info(f"_post_request: {data} | {endpoint}")

        url: str = cls.__BASE_SERVER_URL + endpoint
        logger.success(f'URL: {url}'
                       f'\nData: {data}')
        return await PostRequest(data=data, url=url).send_request()

    @classmethod
    @logger.catch
    async def _get_request(cls, endpoint: str) -> 'DataStructure':
        """Отправляет запрос к АПИ, и возвращает ответ."""

        logger.info(f"_get_request: {endpoint}")

        url: str = cls.__BASE_SERVER_URL + endpoint
        logger.success(f'URL: {url}')
        return await GetRequest(url=url).send_request()


class UserAPI(API):
    """ Класс для работы с запросами пользователей """

    __URL: str = '/user'

    @classmethod
    @logger.catch
    async def create_user(
            cls: 'UserAPI', telegram_id: int, nick_name: str) -> 'DataStructure':
        """Добавить пользователя"""

        endpoint: str = cls.__URL + '/create_user'
        data = {
            "telegram_id": telegram_id,
            "username": nick_name,
        }
        return await cls._post_request(data=data, endpoint=endpoint)

    @classmethod
    @logger.catch
    async def buy_subscription(
            cls: 'UserAPI', packet: str, telegram_id: str, username: str, price: int) -> dict:
        """Купить подписку"""

        endpoint: str = cls.__URL + '/buy_subscription'
        data = {
            "packet": packet,
            "telegram_id": telegram_id,
            "username": username,
            "price": price
        }
        result: 'DataStructure' = await cls._post_request(data=data, endpoint=endpoint)

        return result.message if result.success else {}

    @classmethod
    @logger.catch
    async def get_current_module(cls: 'UserAPI', telegram_id: int):
        """ Возвращает ссылки модуля для пользователя """

        endpoint: str = cls.__URL + '/get_current_module'
        data = {
            "telegram_id": telegram_id
        }

        result = await cls._post_request(data=data, endpoint=endpoint)
        return result.message

    @classmethod
    @logger.catch
    async def get_module_id(cls, telegram_id: int):
        """ Возвращает ID модуля ученика """

        endpoint: str = cls.__URL + '/get_module_id'
        data = {
            "telegram_id": telegram_id
        }

        result = await cls._post_request(data=data, endpoint=endpoint)
        return result.message

    @classmethod
    @logger.catch
    async def get_user_status(
            cls: 'UserAPI', telegram_id: int) -> dict[str, int]:

        endpoint: str = cls.__URL + '/get_user_status'
        data = {
            "telegram_id": telegram_id,
        }

        result: 'DataStructure' = await cls._post_request(data=data, endpoint=endpoint)
        return result.data

    @classmethod
    @logger.catch
    async def get_id_channel(cls: 'UserAPI', tag: str) -> dict[str, int]:
        """ Возвращаешь ID канала по его тэгу """

        endpoint: str = cls.__URL + '/get_id_channel'
        data: dict = {
            "tag": tag
        }

        result: 'DataStructure' = await cls._post_request(data=data, endpoint=endpoint)
        return result

    @classmethod
    @logger.catch
    async def check_payment(
            cls: 'UserAPI', telegram_id: int, tag: str) -> 'DataStructure':

        endpoint: str = cls.__URL + '/check_payment'
        data: dict = {
            "telegram_id": telegram_id,
            "tag": tag
        }

        return await cls._post_request(data=data, endpoint=endpoint)


class AdminAPI(API):
    """ Класс для работы с admin API """

    __URL: str = '/admin'

    @classmethod
    @logger.catch
    async def activate_user(
            cls: 'AdminAPI', telegram_id: int, tag: str) -> Union[dict, str]:
        """Активировать пользователя"""

        endpoint: str = cls.__URL + '/activate_user'
        data = {
            "telegram_id": telegram_id,
            "tag": tag
        }

        result: 'DataStructure' = await cls._post_request(data=data, endpoint=endpoint)
        return result.data

    @classmethod
    @logger.catch
    async def get_modules(cls) -> Union[list]:
        """ Возвращает список записанных в БД модулей """

        endpoint: str = cls.__URL + "/get_modules"
        result: 'DataStructure' = await cls._get_request(endpoint=endpoint)
        return result

    @classmethod
    @logger.catch
    async def add_module(cls, module_id: int, links: str) -> Union[dict, str]:
        """ Добавляет новый модуль в базу данных """

        endpoint: str = cls.__URL + "/add_module"
        data = {
            "module_id": module_id,
            "links": links
        }

        result: 'DataStructure' = await cls._post_request(endpoint=endpoint, data=data)
        loguru.logger.info(f"результат: {result}")
        return result.data

    @classmethod
    @logger.catch
    async def add_rating(cls, telegram_id: int):
        """ Добавить +1 рэйтинг пользователю """

        endpoint: str = cls.__URL + "/add_rating"
        data = {
            "telegram_id": telegram_id
        }
        result: 'DataStructure' = await cls._post_request(endpoint=endpoint, data=data)
        return result.data

    @classmethod
    @logger.catch
    async def deactivate_user(cls: 'AdminAPI', telegram_id: int) -> Union[dict, str]:
        """ Деактивировать пользователя """

        endpoint: str = cls.__URL + "/deactivate_user"
        data = {
            "telegram_id": telegram_id
        }
        result: 'DataStructure' = await cls._post_request(data=data, endpoint=endpoint)
        return result.data

    @classmethod
    @logger.catch
    async def get_active_users(cls: 'AdminAPI') -> list[dict]:
        """ Получить список пользователей которые могут находиться в чате """

        # TODO: Need to test
        endpoint: str = cls.__URL + '/get_active_users'
        result: 'DataStructure' = await cls._get_request(endpoint=endpoint)
        return result if isinstance(result, list) else []

    @classmethod
    @logger.catch
    async def get_all_users(cls: 'AdminAPI') -> list[dict]:
        """ Получает список всех пользователей из базы данных """

        endpoint: str = cls.__URL + '/get_user_list'
        result: list[UserModel] = await cls._get_request(endpoint=endpoint)

        return result

    @classmethod
    @logger.catch
    async def add_channel(
            cls: 'AdminAPI', channel_id: int, tag: str) -> 'DataStructure':
        """ Добавить канал """

        endpoint: str = cls.__URL + '/add_channel'
        data = {
            "channel_id": channel_id,
            "tag": tag,
        }
        return await cls._post_request(data=data, endpoint=endpoint)

    @classmethod
    @logger.catch
    async def get_channels(cls) -> 'DataStructure':
        """ Получить каналы для кика пользователей """

        endpoint: str = cls.__URL + '/get_channels'
        return await cls._get_request(endpoint=endpoint)


class RootAPI(API):
    """ Класс для работы с ROOT API """

    __URL: str = '/root'

    @classmethod
    @logger.catch
    async def change_price(
            cls: 'RootAPI', status: str, new_price: int) -> 'DataStructure':
        """ Изменить цену подписки """

        endpoint: str = cls.__URL + '/sub_price'
        data: dict = {
            "status": status,
            "new_price": new_price
        }
        return await cls._post_request(data=data, endpoint=endpoint)
