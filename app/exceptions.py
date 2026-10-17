from typing import TYPE_CHECKING

from fastapi.responses import JSONResponse
from sqlalchemy import exc as sa_exc
from starlette import status


if TYPE_CHECKING:
    from advanced_alchemy.exceptions import DuplicateKeyError, ForeignKeyError, NotFoundError
    from starlette.requests import Request


async def duplicate_key_error_handler(_: Request, exc: DuplicateKeyError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": exc.detail},
    )


async def not_found_error_handler(_: Request, __: NotFoundError | ForeignKeyError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Not found"},
    )


async def database_unavailable_handler(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, sa_exc.TimeoutError) and not isinstance(exc.__cause__, sa_exc.TimeoutError):
        raise exc
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database unavailable"},
    )
