import dataclasses
import logging
import re
import typing

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext import asyncio as sa_async
from sqlalchemy.orm import selectinload

from app import models
from app.db.helpers import operators_map
from app.exceptions import DatabaseValidationError


logger = logging.getLogger(__name__)
T = typing.TypeVar("T", bound=models.BaseModel)


@dataclasses.dataclass(kw_only=True)
class BaseRepository(typing.Generic[T]):
    model: type[T] = dataclasses.field(init=False)
    session: sa_async.AsyncSession

    def _raise_validation_exception(self, exception: IntegrityError) -> typing.Never:
        info = exception.orig.args[0] if exception.orig.args else ""  # type: ignore[union-attr]
        if (match := re.findall(r"Key \((.*)\)=\(.*\) already exists|$", info)) and match[0]:
            msg = f"Unique constraint violated for {self.model.__name__}"
            raise DatabaseValidationError(msg, match[0]) from exception
        if (match := re.findall(r"Key \((.*)\)=\(.*\) conflicts with existing key|$", info)) and match[0]:
            field_name = match[0].split(",", 1)[0]
            msg = f"Range overlapped for {self.model.__name__}"
            raise DatabaseValidationError(msg, field_name) from exception
        if (match := re.findall(r"Key \((.*)\)=\(.*\) is not present in table|$", info)) and match[0]:
            msg = f"Foreign key constraint violated for {self.model.__name__}"
            raise DatabaseValidationError(msg, match[0]) from exception
        logger.error("Integrity error for %s: %s", self.model.__name__, exception)
        raise exception

    def _get_query(
        self,
        prefetch: tuple[str, ...] | None = None,
        options: list[typing.Any] | None = None,
    ) -> sa.Select[tuple[T]]:
        query = sa.select(self.model)
        if prefetch:
            if not options:
                options = []
            options.extend(selectinload(getattr(self.model, x)) for x in prefetch)
            query = query.options(*options).execution_options(populate_existing=True)
        return query

    async def all(self, prefetch: tuple[str, ...] | None = None) -> typing.Sequence[T]:
        query = self._get_query(prefetch)
        result_cursor = await self.session.execute(query)
        return result_cursor.scalars().all()

    async def get_by_id(self, obj_id: int, prefetch: tuple[str, ...] | None = None) -> T | None:
        query = self._get_query(prefetch).where(self.model.id == obj_id)
        result_cursor = await self.session.execute(query)
        return result_cursor.scalars().first()

    async def filter(
        self,
        filters: dict[str, typing.Any],
        sorting: dict[str, str] | None = None,
        prefetch: tuple[str, ...] | None = None,
    ) -> typing.Sequence[T]:
        query = self._get_query(prefetch)
        if sorting is not None:
            query = query.order_by(*self._build_sorting(sorting))
        db_execute = await self.session.execute(query.where(sa.and_(True, *self._build_filters(filters))))
        return db_execute.scalars().all()

    def _build_sorting(self, sorting: dict[str, str]) -> list[typing.Any]:
        """Build list of ORDER_BY clauses."""
        result = []
        for field_name, direction in sorting.items():
            field = getattr(self.model, field_name)
            result.append(getattr(field, direction)())
        return result

    def _build_filters(self, filters: dict[str, typing.Any]) -> list[typing.Any]:
        """Build list of WHERE conditions."""
        result = []
        for expression, value in filters.items():
            parts = expression.split("__")
            op_name = parts[1] if len(parts) > 1 else "exact"
            if op_name not in operators_map:
                msg = f"Expression {expression} has incorrect operator {op_name}"
                raise KeyError(msg)
            operator = operators_map[op_name]
            column = getattr(self.model, parts[0])
            result.append(operator(column, value))
        return result

    async def bulk_create(self, objects: list[T]) -> typing.Sequence[T]:
        try:
            self.session.add_all(objects)
            await self.session.flush()
        except IntegrityError as e:
            self._raise_validation_exception(e)
        return objects

    async def bulk_update(self, objects: list[T]) -> typing.Sequence[T]:
        try:
            ids = [x.id for x in objects if x.id]
            await self.session.execute(sa.select(self.model).where(self.model.id.in_(ids)))
            for item in objects:
                try:
                    await self.session.merge(item)
                except IntegrityError as e:
                    self._raise_validation_exception(e)
            await self.session.flush()
        except IntegrityError as e:
            self._raise_validation_exception(e)
        return objects

    async def save(self, instance: T, commit: bool = True) -> None:
        self.session.add(instance)
        try:
            if commit:
                await self.session.commit()
            else:
                await self.session.flush()
        except IntegrityError as e:
            self._raise_validation_exception(e)

    @staticmethod
    async def update_attrs(instance: T, **kwargs: typing.Any) -> None:  # noqa: ANN401
        for k, v in kwargs.items():
            setattr(instance, k, v)
