import dataclasses
import typing
from collections.abc import Sequence

from db_retry import Transaction, postgres_retry

from app import models, schemas
from app.repositories import CardsRepository


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class CreateCardsUseCase:
    transaction: Transaction
    cards_repository: CardsRepository

    @postgres_retry
    async def __call__(self, *, deck_id: int, data: list[schemas.CardCreate]) -> Sequence[models.Card]:
        async with self.transaction:
            cards: typing.Final = await self.cards_repository.add_cards(deck_id, data)
            await self.transaction.commit()
        return cards
