import dataclasses
import typing
from collections.abc import Sequence

from db_retry import Transaction, postgres_retry

from app import models
from app.repositories import CardsRepository


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class ListCardsUseCase:
    transaction: Transaction
    cards_repository: CardsRepository

    @postgres_retry
    async def __call__(self, *, deck_id: int, after: int | None, limit: int) -> Sequence[models.Card]:
        async with self.transaction:
            cards: typing.Final = await self.cards_repository.list_for_deck(deck_id, after=after, limit=limit)
            await self.transaction.commit()
        return cards
