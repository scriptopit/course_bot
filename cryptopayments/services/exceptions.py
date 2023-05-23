from fastapi import HTTPException
from starlette import status

exception_unauthorized = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Access denied'
)


exception_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Error data'
)


wallet_error = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail='Wallet exists'
)


UserExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='User exists'
)


UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='User not found'
)


WrongVersionException = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail='Wrong version'
)

WrongBuildException = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail='Wrong build'
)

ChannelExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Channel exists'
)
