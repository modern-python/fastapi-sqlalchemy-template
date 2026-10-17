import asyncio
import logging
import typing

import fastapi
from sqlalchemy.engine.interfaces import IsolationLevel
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.ext import asyncio as sa

from app.settings import settings


logger = logging.getLogger(__name__)


READ_METHODS: typing.Final = frozenset({"GET", "HEAD"})


def create_sa_engine(url: URL, *, read_only: bool = False) -> sa.AsyncEngine:
    return sa.create_async_engine(
        url=url,
        echo=settings.service_debug,
        echo_pool=settings.service_debug,
        pool_size=settings.db_pool_size,
        pool_pre_ping=settings.db_pool_pre_ping,
        max_overflow=settings.db_max_overflow,
        isolation_level="AUTOCOMMIT" if read_only else None,
        connect_args={"server_settings": {"default_transaction_read_only": "on"}} if read_only else {},
    )


def create_primary_sa_engine() -> sa.AsyncEngine:
    return create_sa_engine(settings.db_dsn_parsed)


def create_read_sa_engine() -> sa.AsyncEngine:
    return create_sa_engine(
        make_url(settings.db_replica_dsn) if settings.db_replica_dsn else settings.db_dsn_parsed,
        read_only=True,
    )


def autocommit_isolation_level() -> IsolationLevel | None:
    return "AUTOCOMMIT"


async def close_sa_engine(engine: sa.AsyncEngine) -> None:
    await engine.dispose()


def choose_sa_engine(
    *,
    primary_engine: sa.AsyncEngine,
    read_engine: sa.AsyncEngine,
    request: fastapi.Request | None = None,
) -> sa.AsyncEngine:
    if request and request.method in READ_METHODS:
        return read_engine
    return primary_engine


def create_session(engine: sa.AsyncEngine | sa.AsyncConnection) -> sa.AsyncSession:
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
