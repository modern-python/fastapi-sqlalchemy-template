from advanced_alchemy.exceptions import DuplicateKeyError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.requests import Request


async def duplicate_key_error_handler(_: Request, exc: DuplicateKeyError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.detail},
    )
