import pydantic
from pydantic import BaseModel, PositiveInt


class Base(BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


class CardBase(Base):
    front: str
    back: str | None = None
    hint: str | None = None


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: PositiveInt
    deck_id: PositiveInt | None = None


class Cards(Base):
    items: list[Card]


class DeckBase(Base):
    name: str
    description: str | None = None


class DeckCreate(DeckBase):
    pass


class Deck(DeckBase):
    id: PositiveInt
    cards: list[Card] | None


class Decks(Base):
    items: list[Deck]
