from config import db
from tortoise.contrib.fastapi import register_tortoise


def db_connect(app) -> None:
    register_tortoise(
        app,
        db_url=db.get_db_name(),
        modules={"models": ["models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
