import dataclasses
import typing

from db_retry import Transaction, postgres_retry

from app import models
from app.repositories import CardsRepository


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class GetCardUseCase:
    transaction: Transaction
    cards_repository: CardsRepository

    @postgres_retry
    async def __call__(self, *, card_id: int) -> models.Card:
        async with self.transaction:
            card: typing.Final = await self.cards_repository.get_one(models.Card.id == card_id)
            await self.transaction.commit()
        return card
