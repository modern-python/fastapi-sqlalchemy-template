import operator
from typing import TYPE_CHECKING

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy import orm

from app import models, schemas


if TYPE_CHECKING:
    from collections.abc import Sequence


class DecksRepository(SQLAlchemyAsyncRepositoryService[models.Deck]):
    class BaseRepository(SQLAlchemyAsyncRepository[models.Deck]):
        model_type = models.Deck

    repository_type = BaseRepository

    async def list_decks(self) -> Sequence[models.Deck]:
        return await self.get_many(order_by=models.Deck.id.asc())

    async def fetch_with_cards(self, deck_id: int) -> models.Deck:
        return await self.get_one(
            models.Deck.id == deck_id,
            load=[orm.selectinload(models.Deck.cards)],
        )


class CardsRepository(SQLAlchemyAsyncRepositoryService[models.Card]):
    class BaseRepository(SQLAlchemyAsyncRepository[models.Card]):
        model_type = models.Card

    repository_type = BaseRepository

    async def list_for_deck(self, deck_id: int) -> Sequence[models.Card]:
        return await self.get_many(models.Card.deck_id == deck_id, order_by=models.Card.id.asc())

    async def add_cards(self, deck_id: int, cards: list[schemas.CardCreate]) -> Sequence[models.Card]:
        return await self.create_many([models.Card(**card.model_dump(), deck_id=deck_id) for card in cards])

    async def upsert_cards(self, deck_id: int, cards: list[schemas.Card]) -> Sequence[models.Card]:
        upserted = await self.upsert_many(
            [models.Card(**card.model_dump(exclude={"deck_id"}), deck_id=deck_id) for card in cards],
        )
        return sorted(upserted, key=operator.attrgetter("id"))
