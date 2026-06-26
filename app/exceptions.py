from typing import TYPE_CHECKING

from fastapi.responses import JSONResponse
from starlette import status


if TYPE_CHECKING:
    from advanced_alchemy.exceptions import DuplicateKeyError, NotFoundError
    from starlette.requests import Request


async def duplicate_key_error_handler(_: Request, exc: DuplicateKeyError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": exc.detail},
    )


async def not_found_error_handler(_: Request, __: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Not found"},
    )
