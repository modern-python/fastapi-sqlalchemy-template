import dataclasses

from db_retry import Transaction, postgres_retry

from app import models, schemas
from app.repositories import DecksRepository


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class CreateDeckUseCase:
    transaction: Transaction
    decks_repository: DecksRepository

    @postgres_retry
    async def __call__(self, *, data: schemas.DeckCreate) -> models.Deck:
        async with self.transaction:
            deck = await self.decks_repository.fetch_by_idempotency_key(data.idempotency_key)
            if deck is None:
                deck = await self.decks_repository.create(data.model_dump())
            await self.transaction.commit()
        return deck
