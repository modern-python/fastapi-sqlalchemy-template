from typing import TYPE_CHECKING, Self

import pydantic
from pydantic import BaseModel, PositiveInt


if TYPE_CHECKING:
    from collections.abc import Iterable


class Base(BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


class Collection[T: Base](Base):
    items: list[T]

    @classmethod
    def from_models(cls, objects: Iterable[object]) -> Self:
        return cls.model_validate({"items": list(objects)})


class CardBase(Base):
    front: str
    back: str | None = None
    hint: str | None = None


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: PositiveInt
    deck_id: PositiveInt | None = None


class Cards(Collection[Card]):
    pass


class DeckBase(Base):
    name: str
    description: str | None = None


class DeckCreate(DeckBase):
    pass


class Deck(DeckBase):
    """Light deck view for lists and writes; cards are not loaded."""

    id: PositiveInt


class DeckWithCards(Deck):
    """Deck detail view; cards are eager-loaded (selectinload) and always present."""

    cards: list[Card]


class Decks(Collection[Deck]):
    pass
