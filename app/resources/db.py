import asyncio
import logging
import typing

from sqlalchemy.ext import asyncio as sa

from app.settings import settings


logger = logging.getLogger(__name__)


def create_sa_engine() -> sa.AsyncEngine:
    return sa.create_async_engine(
        url=settings.db_dsn_parsed,
        echo=settings.service_debug,
        echo_pool=settings.service_debug,
        pool_size=settings.db_pool_size,
        pool_pre_ping=settings.db_pool_pre_ping,
        max_overflow=settings.db_max_overflow,
    )


async def close_sa_engine(engine: sa.AsyncEngine) -> None:
    await engine.dispose()


def create_session(engine: sa.AsyncEngine) -> sa.AsyncSession:
    # join_transaction_mode is inert in production (the session binds to an engine); when tests bind
    # the session to a connection already in a transaction, it makes the session own a savepoint so
    # the outer transaction survives commits and the per-test rollback stays clean.
    return sa.AsyncSession(
        engine,
        expire_on_commit=False,
        autoflush=False,
        join_transaction_mode="create_savepoint",
    )


async def close_session(session: sa.AsyncSession) -> None:
    task: typing.Final = asyncio.create_task(session.close())
    await asyncio.shield(task)
