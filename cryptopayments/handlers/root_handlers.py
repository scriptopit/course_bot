from fastapi import APIRouter, Request


root_router = APIRouter()


@root_router.get('/my_ip', tags=['root'])
def my_ip(request: Request):
    return request.client.host