import contextlib
import typing

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Session
from app.ioc import IOCContainer


@contextlib.asynccontextmanager
async def session_context() -> typing.AsyncIterator[None]:
    engine = await IOCContainer.database_engine()
    async with AsyncSession(engine, expire_on_commit=False, autoflush=False) as _session:
        token = Session.set(_session)
        try:
            yield
        finally:
            Session.reset(token)
