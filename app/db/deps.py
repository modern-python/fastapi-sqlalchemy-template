import typing
from contextvars import ContextVar

from sqlalchemy.ext import asyncio as sa_async

from app.db.base import async_session


session_context_var: ContextVar[sa_async.AsyncSession | None] = ContextVar("_session", default=None)


async def set_db() -> typing.AsyncIterator[None]:
    """Store db session in the context var and reset it."""
    db = async_session()
    token = session_context_var.set(db)
    try:
        yield
    finally:
        await db.close()
        session_context_var.reset(token)


def get_db() -> sa_async.AsyncSession:
    """Fetch db session from the context var."""
    session = session_context_var.get()
    if session is None:
        msg = "Missing session"
        raise RuntimeError(msg)
    return session
