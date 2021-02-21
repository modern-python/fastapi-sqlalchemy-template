import re
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import as_declarative, declared_attr

from app.config import settings


engine = create_async_engine(settings.DB_DSN)


class DatabaseValidationError(Exception):
    def __init__(self, message: str, field: Optional[str] = None) -> None:
        self.message = message
        self.field = field


class ObjectDoesNotExist(Exception):
    pass


@as_declarative()
class Base:
    id = sa.Column(sa.Integer, primary_key=True, index=True)

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return cls.__name__.lower()  # pylint: disable=no-member

    @classmethod
    async def all(cls, db: AsyncSession):
        db_execute = await db.execute(sa.select(cls))
        return db_execute.scalars().all()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, object_id: int):
        db_execute = await db.execute(sa.select(cls).where(cls.id == object_id))
        instance = db_execute.scalars().first()
        if instance is None:
            raise ObjectDoesNotExist
        return instance

    async def save(self, db):
        db.add(self)
        try:
            await db.commit()
        except IntegrityError as e:
            info = e.orig.args
            m = re.findall(r"Key \((.*)\)=\(.*\) already exists|$", info[0])
            raise DatabaseValidationError(
                f"{type(self).__name__} already exists", m[0] if m else None
            )
        await db.refresh(self)
