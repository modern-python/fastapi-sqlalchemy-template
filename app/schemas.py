import uuid
from typing import TYPE_CHECKING, Annotated, Final, Protocol, Self

import pydantic
from pydantic import BaseModel, Field, PositiveInt


if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


DEFAULT_PAGE_LIMIT: Final = 50
MAX_PAGE_LIMIT: Final = 100
MAX_CARDS_PER_REQUEST: Final = 1000
MAX_ID: Final = 2**63 - 1

Id = Annotated[int, Field(gt=0, le=MAX_ID)]


class HasId(Protocol):
    id: int


class Base(BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


class Collection[T: Base](Base):
    items: list[T]

    @classmethod
    def from_models(cls, objects: Iterable[object]) -> Self:
        return cls.model_validate({"items": list(objects)})


class Page[T: Base](Base):
    items: list[T]
    next_after: PositiveInt | None

    @classmethod
    def from_models(cls, objects: Sequence[HasId], *, limit: int) -> Self:
        has_next: Final = len(objects) > limit
        return cls.model_validate(
            {"items": list(objects[:limit]), "next_after": objects[limit - 1].id if has_next else None}
        )


class CardBase(Base):
    front: str
    back: str | None = None
    hint: str | None = None


class CardCreate(CardBase):
    pass


class CardUpdate(CardBase):
    id: Id


def _ensure_unique_ids(cards: list[CardUpdate]) -> list[CardUpdate]:
    if len({card.id for card in cards}) != len(cards):
        msg = "card ids must be unique"
        raise ValueError(msg)
    return cards


CardCreates = Annotated[list[CardCreate], Field(max_length=MAX_CARDS_PER_REQUEST)]
CardUpdates = Annotated[
    list[CardUpdate], Field(max_length=MAX_CARDS_PER_REQUEST), pydantic.AfterValidator(_ensure_unique_ids)
]


class Card(CardUpdate):
    deck_id: PositiveInt


class Cards(Collection[Card]):
    pass


class CardsPage(Page[Card]):
    pass


class DeckBase(Base):
    name: str
    description: str | None = None


class DeckCreate(DeckBase):
    idempotency_key: uuid.UUID


class DeckUpdate(DeckBase):
    pass


class Deck(DeckBase):
    """Light deck view for lists and writes; cards are not loaded."""

    id: PositiveInt


class DeckWithCards(Deck):
    """Deck detail view; cards are eager-loaded (joinedload) and always present."""

    cards: list[Card]


class DecksPage(Page[Deck]):
    pass
