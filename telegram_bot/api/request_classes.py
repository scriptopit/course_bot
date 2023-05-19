import asyncio
import aiohttp
import aiohttp.client_exceptions
import aiohttp.http_exceptions

from config import DB_KEY_VALIDATION
from api.utils import DataStructure
from classes.errors_reporter import MessageReporter
from abc import abstractmethod, ABC
from config import logger


class RequestSender(ABC):

    def __init__(self, url: str = ""):
        self.url: str = url
        self._payload: dict = {}

    @abstractmethod
    async def _send(self, *args, **kwargs):
        pass

    async def send_request(self) -> 'DataStructure':
        self._payload: dict = {
            'url': self.url
        }
        headers: dict = {
            "token": DB_KEY_VALIDATION
        }
        text: str = ""
        session_params: dict = {
            "trust_env": True,
            "connector": aiohttp.TCPConnector(),
            "headers": headers
        }
        answer: dict = {}

        try:
            async with aiohttp.ClientSession(**session_params) as session:
                answer: dict = await self._send(session)

        except aiohttp.client_exceptions.ClientConnectorError as err:
            logger.error(f"aiohttp.client_exceptions.ClientConnectorError: {err}")
            answer.update(status=407, err=err)
        except aiohttp.http_exceptions.BadHttpMessage as err:
            logger.error(f"aiohttp.http_exceptions.BadHttpMessage: {err}")
            answer.update(status=407, err=err)
        except aiohttp.client_exceptions.ClientHttpProxyError as err:
            logger.error(f"aiohttp.client_exceptions.ClientHttpProxyError: {err}")
            answer.update(status=407, err=err)
        except asyncio.exceptions.TimeoutError as err:
            logger.error(f"asyncio.exceptions.TimeoutError: {err}")
            answer.update(status=-99, err=err)
        except aiohttp.client_exceptions.ClientOSError as err:
            logger.error(f"aiohttp.client_exceptions.ClientOSError: {err}")
            answer.update(status=-98, err=err)
        except aiohttp.client_exceptions.ServerDisconnectedError as err:
            logger.error(f"aiohttp.client_exceptions.ServerDisconnectedError: {err}")
            answer.update(status=-97, err=err)
        except aiohttp.client_exceptions.TooManyRedirects as err:
            logger.error(f"aiohttp.client_exceptions.TooManyRedirects: {err}")
            answer.update(status=-96, err=err)
        except aiohttp.client_exceptions.ContentTypeError as err:
            logger.error(f"aiohttp.client_exceptions.ContentTypeError: {err}")
            answer.update(status=-95, err=err)
        except Exception as err:
            text = f"Exception: {err}"
            answer.update(status=-100, err=err)
            logger.error(text)

        status = answer.get("status")
        logger.success(f"{answer}")

        if status == 204:
            return DataStructure(status=status, data={}, message="No content")
        elif status in range(400, 500):
            return DataStructure(status=status, data={}, message=f"Error {status}")
        elif status not in range(200, 300):
            error_text: str = (
                f"\nStatus: {status}"
                f"\nUrl: {self.url}"
            )
            logger.error(error_text)
            answer: dict = await MessageReporter(answer=answer).handle_errors()

        data: dict = answer.get("answer_data")
        logger.info(f"========= {data}")
        if data and isinstance(data, dict):
            if all((data.get("status"), data.get("code"))):
                return DataStructure(**data)

        return DataStructure(status=status, data=data)


class GetRequest(RequestSender):
    async def _send(self, session) -> dict:
        """ Отправляет GET запрос """

        async with session.get(**self._payload) as response:
            return {
                "status": response.status,
                "answer_data": await response.json()
            }


class PostRequest(RequestSender):

    def __init__(self, data: dict = None, url: str = ""):
        super().__init__(url)
        self._data_for_send: dict = data

    async def _send(self, session) -> dict:
        """ Отправляет POST запрос """

        self._payload.update(json=self._data_for_send)
        print(self._payload)
        async with session.post(**self._payload) as response:
            return {
                "status": response.status,
                "answer_data": await response.json()
            }
