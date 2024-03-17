from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.db.exceptions import DatabaseValidationError


async def database_validation_exception_handler(request: Request, exc: DatabaseValidationError) -> JSONResponse:
    validation_error = RequestValidationError(
        [
            {
                "loc": [exc.field or "__root__"],
                "msg": exc.message,
                "input": {},
                "ctx": {"error": exc.message},
            },
        ],
        body=exc.message,
    )
    return await request_validation_exception_handler(request, validation_error)
