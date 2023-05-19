from fastapi import APIRouter
from handlers.user_handlers import user_router
from handlers.root_handlers import root_router
from handlers.admin_handlers import admin_router


api_router = APIRouter(prefix="/api/v1/cryptopayments")
api_router.include_router(user_router, prefix="/user")
api_router.include_router(admin_router, prefix="/admin")
api_router.include_router(root_router, prefix="/root")
