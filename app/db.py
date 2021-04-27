import logging
import re
from typing import Any, List, NoReturn, Optional, Type, TypeVar

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


logger = logging.getLogger(__name__)
engine = create_async_engine(
    settings.DB_DSN,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    future=True,
)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, future=True
)
metadata = MetaData()
_Base = declarative_base(metadata=metadata)


class DatabaseValidationError(Exception):
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        object_id: Optional[int] = None,
    ) -> None:
        self.message = message
        self.field = field
        self.object = object_id


# https://mypy.readthedocs.io/en/latest/generics.html#generic-methods-and-generic-self
T = TypeVar("T", bound="Base")


class Base(_Base):  # type: ignore
    __abstract__ = True

    id = sa.Column(sa.Integer, primary_key=True, index=True)

    @classmethod
    def _raise_validation_exception(
        cls, e: IntegrityError, object_id: Optional[int] = None
    ) -> NoReturn:
        info = e.orig.args
        match: List[str] = re.findall(
            r"Key \((.*)\)=\(.*\) already exists|$", info[0]
        )
        if match:
            raise DatabaseValidationError(
                f"Unique constraint violated for {cls.__name__}",
                field=match[0],
                object_id=object_id,
            ) from e
        raise DatabaseValidationError(
            f"Integrity error for {cls.__name__}", object_id=object_id
        ) from e

    @classmethod
    async def all(cls: Type[T], db: AsyncSession) -> List[T]:
        db_execute = await db.execute(sa.select(cls))
        return db_execute.scalars().all()

    @classmethod
    async def filter(
        cls: Type[T], db: AsyncSession, conditions: List[Any]
    ) -> List[T]:
        query = sa.select(cls)
        db_execute = await db.execute(query.where(sa.and_(*conditions)))
        return db_execute.scalars().all()

    @classmethod
    async def get_by_id(cls: Type[T], db: AsyncSession, object_id: int) -> T:
        return await db.get(cls, object_id)

    @classmethod
    async def bulk_create(
        cls: Type[T], db: AsyncSession, objects: List[T]
    ) -> List[T]:
        try:
            db.add_all(objects)
            await db.flush()
        except IntegrityError as e:
            cls._raise_validation_exception(e)
        return objects

    @classmethod
    async def bulk_update(
        cls: Type[T], db: AsyncSession, objects: List[T]
    ) -> List[T]:
        try:
            ids = [x.id for x in objects if x.id]
            await db.execute(sa.select(cls).where(cls.id.in_(ids)))
            for item in objects:
                try:
                    await db.merge(item)
                except IntegrityError as e:
                    cls._raise_validation_exception(e, item.id)
            await db.flush()
        except IntegrityError as e:
            cls._raise_validation_exception(e)
        return objects

    async def save(self, db: AsyncSession) -> None:
        db.add(self)
        try:
            await db.flush()
        except IntegrityError as e:
            self._raise_validation_exception(e)

    async def update(self, db: AsyncSession, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
        await self.save(db)
