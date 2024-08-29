from advanced_alchemy.exceptions import ForeignKeyError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request


async def database_validation_exception_handler(request: Request, exc: ForeignKeyError) -> JSONResponse:
    validation_error = RequestValidationError(
        [
            {
                "loc": ["__root__"],
                "msg": exc.detail,
                "input": {},
                "ctx": {"error": exc.detail},
            },
        ],
        body=exc.detail,
    )
    return await request_validation_exception_handler(request, validation_error)
