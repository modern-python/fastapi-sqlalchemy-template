from fastapi import FastAPI

from app.api.views import router
from app.config import settings


def get_app() -> FastAPI:
    _app = FastAPI(title=settings.SERVICE_NAME, debug=settings.DEBUG)

    _app.include_router(router, prefix="/api")

    return _app


app = get_app()
