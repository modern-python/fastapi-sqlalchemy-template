import dataclasses
import typing

from db_retry import Transaction, postgres_retry

from app import models
from app.repositories import DecksRepository


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class GetDeckUseCase:
    transaction: Transaction
    decks_repository: DecksRepository

    @postgres_retry
    async def __call__(self, *, deck_id: int) -> models.Deck:
        async with self.transaction:
            deck: typing.Final = await self.decks_repository.fetch_with_cards(deck_id)
            await self.transaction.commit()
        return deck
