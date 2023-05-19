from fastapi import FastAPI

from routers import api_router
from database.db_connect import db_connect
from config import logger, settings
from migrating import migrate
from services.utils import send_message_to_admins
from _resources import __version__, __appname__, __build__


@logger.catch
def get_application() -> FastAPI:
    """Start func"""

    try:
        migrate()
    except AttributeError as err:
        logger.error(f"Attribute error: {err}")
    except Exception as err:
        logger.error(f"Migration error: {err}")
    send_message_to_admins(f"{__appname__} started."
                           f"\nBuild: [{__build__}]"
                           f"\nVersion: [{__version__}]"
                           f"\nLocation: [{settings.LOCATION}]"
    )
    application = FastAPI()
    db_connect(application)
    application.include_router(api_router)

    return application


app = get_application()
