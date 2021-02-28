from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ErrorWrapper
from starlette import status

from app.db import DatabaseValidationError


async def database_validation_exception_handler(
    request, exc: DatabaseValidationError
) -> JSONResponse:
    return await request_validation_exception_handler(
        request,
        RequestValidationError(
            [ErrorWrapper(ValueError(exc.message), exc.field or "__root__")]
        ),
    )


async def object_does_not_exist_exception_handler(request, exc) -> JSONResponse:
    return await http_exception_handler(
        request, HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    )
