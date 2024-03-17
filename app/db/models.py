import datetime
import logging
import re
import typing

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.deps import get_db
from app.db.exceptions import DatabaseValidationError
from app.db.utils import operators_map
from app.utils.datetime import generate_utc_dt


if typing.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


METADATA: typing.Final = sa.MetaData()


class Base(orm.DeclarativeBase):
    metadata = METADATA


class EmptyBaseModel(Base):
    __abstract__ = True


class BaseModel(Base):
    __abstract__ = True

    id: orm.Mapped[typing.Annotated[int, orm.mapped_column(primary_key=True)]]
    created_at: orm.Mapped[
        typing.Annotated[
            datetime.datetime,
            orm.mapped_column(sa.DateTime(timezone=True), default=generate_utc_dt, nullable=False),
        ]
    ]
    updated_at: orm.Mapped[
        typing.Annotated[
            datetime.datetime,
            orm.mapped_column(sa.DateTime(timezone=True), default=generate_utc_dt, nullable=False),
        ]
    ]

    def __str__(self) -> str:
        return f"<{type(self).__name__}({self.id=})>"

    @classmethod
    def _raise_validation_exception(cls, e: IntegrityError) -> typing.Never:
        info = e.orig.args[0] if e.orig.args else ""  # type: ignore[union-attr]
        if (match := re.findall(r"Key \((.*)\)=\(.*\) already exists|$", info)) and match[0]:
            msg = f"Unique constraint violated for {cls.__name__}"
            raise DatabaseValidationError(msg, match[0]) from e
        if (match := re.findall(r"Key \((.*)\)=\(.*\) conflicts with existing key|$", info)) and match[0]:
            field_name = match[0].split(",", 1)[0]
            msg = f"Range overlapped for {cls.__name__}"
            raise DatabaseValidationError(msg, field_name) from e
        if (match := re.findall(r"Key \((.*)\)=\(.*\) is not present in table|$", info)) and match[0]:
            msg = f"Foreign key constraint violated for {cls.__name__}"
            raise DatabaseValidationError(msg, match[0]) from e
        logger.error("Integrity error for %s: %s", cls.__name__, e)
        raise e

    @classmethod
    def _get_query(
        cls,
        prefetch: tuple[str, ...] | None = None,
        options: list[typing.Any] | None = None,
    ) -> sa.Select[tuple[typing.Self]]:
        query = sa.select(cls)
        if prefetch:
            if not options:
                options = []
            options.extend(selectinload(getattr(cls, x)) for x in prefetch)
            query = query.options(*options).execution_options(populate_existing=True)
        return query

    @classmethod
    async def all(cls, prefetch: tuple[str, ...] | None = None) -> typing.Sequence[typing.Self]:
        query = cls._get_query(prefetch)
        db = get_db()
        db_execute = await db.execute(query)
        return db_execute.scalars().all()

    @classmethod
    async def get_by_id(cls, obj_id: int, prefetch: tuple[str, ...] | None = None) -> typing.Self | None:
        query = cls._get_query(prefetch).where(cls.id == obj_id)
        db = get_db()
        db_execute = await db.execute(query)
        return db_execute.scalars().first()

    @classmethod
    async def filter(
        cls,
        filters: dict[str, typing.Any],
        sorting: dict[str, str] | None = None,
        prefetch: tuple[str, ...] | None = None,
    ) -> typing.Sequence[typing.Self]:
        query = cls._get_query(prefetch)
        db = get_db()
        if sorting is not None:
            query = query.order_by(*cls._build_sorting(sorting))
        db_execute = await db.execute(query.where(sa.and_(True, *cls._build_filters(filters))))
        return db_execute.scalars().all()

    @classmethod
    def _build_sorting(cls, sorting: dict[str, str]) -> list[typing.Any]:
        """Build list of ORDER_BY clauses."""
        result = []
        for field_name, direction in sorting.items():
            field = getattr(cls, field_name)
            result.append(getattr(field, direction)())
        return result

    @classmethod
    def _build_filters(cls, filters: dict[str, typing.Any]) -> list[typing.Any]:
        """Build list of WHERE conditions."""
        result = []
        for expression, value in filters.items():
            parts = expression.split("__")
            op_name = parts[1] if len(parts) > 1 else "exact"
            if op_name not in operators_map:
                msg = f"Expression {expression} has incorrect operator {op_name}"
                raise KeyError(msg)
            operator = operators_map[op_name]
            column = getattr(cls, parts[0])
            result.append(operator(column, value))
        return result

    @classmethod
    async def bulk_create(cls, objects: list[typing.Self]) -> typing.Sequence[typing.Self]:
        db: AsyncSession = get_db()
        try:
            db.add_all(objects)
            await db.flush()
        except IntegrityError as e:
            cls._raise_validation_exception(e)
        return objects

    @classmethod
    async def bulk_update(cls, objects: list[typing.Self]) -> typing.Sequence[typing.Self]:
        db: AsyncSession = get_db()
        try:
            ids = [x.id for x in objects if x.id]
            await db.execute(sa.select(cls).where(cls.id.in_(ids)))
            for item in objects:
                try:
                    await db.merge(item)
                except IntegrityError as e:
                    cls._raise_validation_exception(e)
            await db.flush()
        except IntegrityError as e:
            cls._raise_validation_exception(e)
        return objects

    async def save(self, commit: bool = True) -> None:
        db: AsyncSession = get_db()
        db.add(self)
        try:
            if commit:
                await db.commit()
            else:
                await db.flush()
        except IntegrityError as e:
            self._raise_validation_exception(e)

    async def update_attrs(self, **kwargs: typing.Any) -> None:  # noqa: ANN401
        for k, v in kwargs.items():
            setattr(self, k, v)
