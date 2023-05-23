import datetime
from typing import Type

from tortoise import ConfigurationError, fields, models
from enum import Enum


class Statuses(Enum):
    enemy: str = "enemy"
    member: str = "member"
    dead_enemy: str = "dead_enemy"


class EnumField(fields.CharField):

    def __init__(self, enum_type: Type[Enum], **kwargs):
        super().__init__(**kwargs)
        if not issubclass(enum_type, Enum):
            raise ConfigurationError("{} is not a subclass of Enum!".format(enum_type))
        self._enum_type = enum_type

    def to_db_value(self, value: Enum, instance) -> str:
        return value.value

    def to_python_value(self, value: str) -> Enum:
        try:
            return self._enum_type(value)
        except Exception:
            raise ValueError(
                "Database value {} does not exist on Enum {}.".format(value, self._enum_type)
            )


class User(models.Model):
    id = fields.BigIntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, description="Telegram id")
    username = fields.CharField(default="", max_length=50, description="Nickname name")
    created_at = fields.DatetimeField(auto_now_add=True, description="Create date")
    updated_at = fields.DatetimeField(auto_now=True, description="Update date")
    expired_at = fields.DatetimeField(auto_now_add=True, description="Expired date")
    tag = fields.TextField(default="", max_length=50, description="Tag packet")
    status = fields.CharField(default="enemy", max_length=100, description="Member status")
    invoice_id = fields.BigIntField(default=0, description="Invoice id Crypto bot")

    class PydanticMeta:
        table_description = "users"

    def save(self, *args, **kwargs):
        if not self.expired_at:
            self.expired_at = datetime.datetime.utcnow()
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username


class Group(models.Model):
    id = fields.BigIntField(pk=True)
    tag = fields.CharField(unique=True, max_length=100, description="Chat name")
    channel_id = fields.BigIntField(unique=True, description="Channel Id")

    class Meta:
        table_description = "channels"

    def __str__(self):
        return self.tag

