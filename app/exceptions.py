from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ErrorWrapper
from starlette.requests import Request

from app.db.exceptions import DatabaseValidationError


async def database_validation_exception_handler(request: Request, exc: DatabaseValidationError) -> JSONResponse:
    return await request_validation_exception_handler(
        request,
        RequestValidationError([ErrorWrapper(ValueError(exc.message), exc.field or "__root__")]),
    )


class ObjectDoesNotExist(Exception):
    pass
