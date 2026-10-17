import dataclasses
import typing
from collections.abc import Sequence

from db_retry import Transaction, postgres_retry

from app import models
from app.repositories import DecksRepository


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class ListDecksUseCase:
    transaction: Transaction
    decks_repository: DecksRepository

    @postgres_retry
    async def __call__(self, *, after: int | None, limit: int) -> Sequence[models.Deck]:
        async with self.transaction:
            decks: typing.Final = await self.decks_repository.list_decks(after=after, limit=limit)
            await self.transaction.commit()
        return decks
