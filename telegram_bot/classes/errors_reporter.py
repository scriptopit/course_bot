import json
import aiogram.utils.exceptions


from typing import Optional
from json import JSONDecodeError
from config import logger, admins_list, bot


class MessageReporter:
    """Отправляет сообщения об ошибках"""

    def __init__(
            self,
            answer: dict = None,
            telegram_id: str = ''
    ) -> None:
        self._answer: dict = answer if answer else {}
        self._status: int = answer.get("status", 0) if answer else 0
        self._answer_data: str = answer.get("answer_data", {}) if answer else {}
        self._telegram_id: str = telegram_id if telegram_id else ''
        self._code: Optional[int] = None
        self._answer_data_dict: dict = {}

    @logger.catch
    async def handle_errors(self) -> dict:
        """Parse status and data from answer"""

        data = {}
        if self._answer_data and not self._answer_data.startswith('<!'):
            try:
                data: dict = json.loads(self._answer_data)
                if isinstance(data, dict):
                    self._code = data.get("code", 0)
                    self._answer_data_dict = data
            except JSONDecodeError as err:
                logger.error(
                    f"ErrorsSender: answer_handling: JSON ERROR: {err}"
                    f"\nStatus: {self._status}"
                    f"\nAnswer data: {self._answer_data}"
                )
        self._answer.update(answer_data=data)
        if self._status not in range(200, 300):
            await self.send_message_check_token()
        return self._answer

    @logger.catch
    async def send_message_check_token(
            self,
            admins: bool = False,
            users: bool = False
    ) -> None:
        """Sending error messages"""

        text: str = ''
        error_messages = {
            0: f"Ошибка {self._status}",
            -100: f"Ошибка {self._status}",
            400: f"Ошибка {self._status}",
            401: f"Ошибка {self._status}",
            403: f"Ошибка {self._status}",
            404: f"Ошибка {self._status}",
            407: f"Ошибка {self._status}",
            500: f"Ошибка {self._status}",
            504: f"Ошибка {self._status}"
        }

        text = error_messages.get(self._status, f"Unrecognised error! {self._status} {self._code}")
        text = text.format(status=self._status)

        if text:
            if self._telegram_id:
                text += f"\nTelegram_ID: {self._telegram_id}"
            if users and self._telegram_id:
                await self.send_message_to_user(text=text)
            if admins:
                await self.send_report_to_admins(text)

        error_message = (
            f"ErrorsSender get error:"
            f"\n\tTelegram_id: {self._telegram_id}"
            f"\n\tError status: {self._status}"
            f"\n\tError data: {self._answer_data}"
        )
        logger.error(error_message)

    @classmethod
    @logger.catch
    async def send_message_to_user(cls, text: str, telegram_id: str, keyboard=None) -> None:
        """Отправляет сообщение пользователю в телеграм"""

        params: dict = {
            "chat_id": telegram_id,
            "text": text
        }
        if keyboard:
            params.update(reply_markup=keyboard)
        try:
            await bot.send_message(**params)
        except aiogram.utils.exceptions.ChatNotFound:
            logger.error(f"Chat {telegram_id} not found")
        except aiogram.utils.exceptions.BotBlocked as err:
            logger.error(f"Пользователь {telegram_id} заблокировал бота {err}")
        except aiogram.utils.exceptions.CantInitiateConversation as err:
            logger.error(f"Не смог отправить сообщение пользователю {telegram_id}. {err}")
        logger.success(f"Send_message_to_user: {telegram_id}: {text}")

    @classmethod
    @logger.catch
    async def send_report_to_admins(cls, text: str, keyboard=None) -> None:
        """Отправляет сообщение в телеграме всем администраторам из списка"""

        text = f'[Рассылка][Superusers]: {text}'
        for admin_id in admins_list:
            params: dict = {
                "telegram_id": admin_id,
                "text": text
            }
            if keyboard:
                params.update(keyboard=keyboard)
            await cls.send_message_to_user(**params)
