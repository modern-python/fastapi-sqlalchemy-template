from sqlalchemy import MetaData
from sqlalchemy.ext import asyncio as sa_async
from sqlalchemy.orm import declarative_base

from app.settings import settings


engine = sa_async.create_async_engine(
    settings.db_dsn,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    future=True,
)
async_session = sa_async.async_sessionmaker(engine, expire_on_commit=False)
metadata = MetaData()
Base = declarative_base(metadata=metadata)
