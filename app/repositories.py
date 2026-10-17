import operator
import typing
from typing import TYPE_CHECKING

import sqlalchemy as sa
from advanced_alchemy.exceptions import NotFoundError, wrap_sqlalchemy_exception
from advanced_alchemy.repository import DEFAULT_ERROR_MESSAGE_TEMPLATES, SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql

from app import models, schemas


if TYPE_CHECKING:
    from collections.abc import Sequence


class DecksRepository(SQLAlchemyAsyncRepositoryService[models.Deck]):
    class BaseRepository(SQLAlchemyAsyncRepository[models.Deck]):
        model_type = models.Deck

    repository_type = BaseRepository

    async def list_decks(self) -> Sequence[models.Deck]:
        return await self.get_many(order_by=models.Deck.id.asc())

    async def get_or_create(self, data: schemas.DeckCreate) -> models.Deck:
        statement = postgresql.insert(models.Deck).values(**data.model_dump())
        statement = statement.on_conflict_do_update(
            index_elements=[models.Deck.idempotency_key],
            set_={"idempotency_key": statement.excluded.idempotency_key},
        )
        return (await self.repository.session.scalars(statement.returning(models.Deck))).one()

    async def fetch_with_cards(self, deck_id: int) -> models.Deck:
        return await self.get_one(
            models.Deck.id == deck_id,
            load=[orm.joinedload(models.Deck.cards)],
            uniquify=True,
        )

    async def update_deck(self, deck_id: int, data: schemas.DeckUpdate) -> models.Deck:
        statement: typing.Final = (
            sa.update(models.Deck).where(models.Deck.id == deck_id).values(**data.model_dump()).returning(models.Deck)
        )
        deck: typing.Final = (await self.repository.session.scalars(statement)).one_or_none()
        if deck is None:
            raise NotFoundError
        return deck


class CardsRepository(SQLAlchemyAsyncRepositoryService[models.Card]):
    class BaseRepository(SQLAlchemyAsyncRepository[models.Card]):
        model_type = models.Card

    repository_type = BaseRepository

    async def list_for_deck(self, deck_id: int) -> Sequence[models.Card]:
        return await self.get_many(models.Card.deck_id == deck_id, order_by=models.Card.id.asc())

    async def add_cards(self, deck_id: int, cards: list[schemas.CardCreate]) -> Sequence[models.Card]:
        return await self.create_many([models.Card(**card.model_dump(), deck_id=deck_id) for card in cards])

    async def update_cards(self, deck_id: int, cards: list[schemas.CardUpdate]) -> Sequence[models.Card]:
        if not cards:
            return []
        updates: typing.Final = sa.values(
            sa.column("id", sa.BigInteger),
            sa.column("front", sa.String),
            sa.column("back", sa.String),
            sa.column("hint", sa.String),
            name="updates",
        ).data([(card.id, card.front, card.back, card.hint) for card in cards])
        statement: typing.Final = (
            sa.update(models.Card)
            .where(models.Card.id == updates.c.id, models.Card.deck_id == deck_id)
            .values(front=updates.c.front, back=updates.c.back, hint=updates.c.hint, updated_at=sa.func.now())
            .returning(models.Card)
        )
        with wrap_sqlalchemy_exception(error_messages=DEFAULT_ERROR_MESSAGE_TEMPLATES, dialect_name="postgresql"):
            updated: typing.Final = (await self.repository.session.scalars(statement)).all()
        if len(updated) != len(cards):
            raise NotFoundError
        return sorted(updated, key=operator.attrgetter("id"))
