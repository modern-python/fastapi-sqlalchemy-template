import asyncio
import logging
import typing

import fastapi
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.ext import asyncio as sa

from app.settings import settings


logger = logging.getLogger(__name__)


REPLICA_METHODS: typing.Final = frozenset({"GET", "HEAD"})


def create_sa_engine(url: URL) -> sa.AsyncEngine:
    return sa.create_async_engine(
        url=url,
        echo=settings.service_debug,
        echo_pool=settings.service_debug,
        pool_size=settings.db_pool_size,
        pool_pre_ping=settings.db_pool_pre_ping,
        max_overflow=settings.db_max_overflow,
    )


def create_primary_sa_engine() -> sa.AsyncEngine:
    return create_sa_engine(settings.db_dsn_parsed)


def create_replica_sa_engine() -> sa.AsyncEngine | None:
    return create_sa_engine(make_url(settings.db_replica_dsn)) if settings.db_replica_dsn else None


async def close_sa_engine(engine: sa.AsyncEngine | None) -> None:
    if engine:
        await engine.dispose()


def choose_sa_engine(
    *,
    primary_engine: sa.AsyncEngine,
    replica_engine: sa.AsyncEngine | None,
    request: fastapi.Request | None = None,
) -> sa.AsyncEngine:
    if replica_engine and request and request.method in REPLICA_METHODS:
        return replica_engine
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
