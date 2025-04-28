import logging
import typing

from sqlalchemy.ext import asyncio as sa

from app.settings import settings


logger = logging.getLogger(__name__)


async def create_sa_engine() -> typing.AsyncIterator[sa.AsyncEngine]:
    logger.info("Initializing SQLAlchemy engine")
    engine = sa.create_async_engine(
        url=settings.db_dsn_parsed,
        echo=settings.service_debug,
        echo_pool=settings.service_debug,
        pool_size=settings.db_pool_size,
        pool_pre_ping=settings.db_pool_pre_ping,
        max_overflow=settings.db_max_overflow,
    )
    logger.info("SQLAlchemy engine has been initialized")
    try:
        yield engine
    finally:
        await engine.dispose()
        logger.info("SQLAlchemy engine has been cleaned up")


class CustomAsyncSession(sa.AsyncSession):
    async def close(self) -> None:
        if isinstance(self.bind, sa.AsyncConnection):
            return self.expunge_all()

        return await super().close()


async def create_session(engine: sa.AsyncEngine) -> typing.AsyncIterator[sa.AsyncSession]:
    async with CustomAsyncSession(engine, expire_on_commit=False, autoflush=False) as session:
        logger.info("session created")
        yield session
        logger.info("session closed")
