import logging
import re
from typing import Any, List, Optional

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import as_declarative, declared_attr

from app.config import settings


logger = logging.getLogger(__name__)
engine = create_async_engine(settings.DB_DSN)


class DatabaseValidationError(Exception):
    def __init__(
        self, message: str, field: Optional[str] = None, object_id: int = None
    ) -> None:
        self.message = message
        self.field = field
        self.object = object_id


class ObjectDoesNotExist(Exception):
    pass


@as_declarative()
class Base:
    id = sa.Column(sa.Integer, primary_key=True, index=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return cls.__name__.lower()  # pylint: disable=no-member

    @classmethod
    async def all(cls, db: AsyncSession):
        db_execute = await db.execute(sa.select(cls))
        return db_execute.scalars().all()

    @classmethod
    async def filter(cls, db: AsyncSession, conditions: List[Any]):
        query = sa.select(cls)
        db_execute = await db.execute(query.where(sa.and_(*conditions)))
        return db_execute.scalars().all()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, object_id: int):
        db_execute = await db.execute(sa.select(cls).where(cls.id == object_id))
        instance = db_execute.scalars().first()
        if instance is None:
            raise ObjectDoesNotExist
        return instance

    @classmethod
    def _raise_validation_exception(
        cls, e: IntegrityError, object_id: int = None
    ):
        info = e.orig.args
        m = re.findall(r"Key \((.*)\)=\(.*\) already exists|$", info[0])
        raise DatabaseValidationError(
            f"Unique constraint violated for {cls.__name__}",
            m[0] if m else None,
            object_id,
        )

    @classmethod
    async def bulk_create(cls, db: AsyncSession, objects: List["Base"]):
        db.add_all(objects)
        try:
            await db.flush()
        except IntegrityError as e:
            cls._raise_validation_exception(e)

    @classmethod
    async def bulk_update(cls, db: AsyncSession, objects: List["Base"]):
        ids = [x.id for x in objects if x.id]
        await db.execute(sa.select(cls).where(cls.id.in_(ids)))
        for x in objects:
            try:
                await db.merge(x)
            except IntegrityError as e:
                cls._raise_validation_exception(e, x.id)
        try:
            await db.flush()
        except IntegrityError as e:
            cls._raise_validation_exception(e)

    async def save(self, db: AsyncSession):
        db.add(self)
        try:
            await db.flush()
        except IntegrityError as e:
            self._raise_validation_exception(e)
        await db.refresh(self)

    async def update(self, db, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        await self.save(db)
