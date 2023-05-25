from pydantic import BaseModel
from typing import Union


class DataStructure(BaseModel):
    status: int = 200
    code: str = '000000'
    success: bool = False
    message: str = ''
    data: dict = {}

    def as_dict(self) -> dict:
        return self.__dict__


class UserModel(BaseModel):
    telegram_id: int
    username: str
    created_at: str
    updated_at: str
    expired_at: str
    tag: str
    status: str

    def as_dict(self) -> dict:
        return self.__dict__
