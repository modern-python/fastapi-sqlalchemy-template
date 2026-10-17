import dataclasses
import typing

from db_retry import Transaction, postgres_retry

from app import models, schemas
from app.repositories import DecksRepository


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class UpdateDeckUseCase:
    transaction: Transaction
    decks_repository: DecksRepository

    @postgres_retry
    async def __call__(self, *, deck_id: int, data: schemas.DeckUpdate) -> models.Deck:
        async with self.transaction:
            deck: typing.Final = await self.decks_repository.update_deck(deck_id, data)
            await self.transaction.commit()
        return deck
