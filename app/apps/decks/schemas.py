from typing import List, Optional

from pydantic import BaseModel, PositiveInt


class Base(BaseModel):
    class Config:
        orm_mode = True


class CardBase(Base):
    front: str
    back: Optional[str] = None
    hint: Optional[str] = None


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: PositiveInt
    deck_id: Optional[PositiveInt] = None


class Cards(Base):
    items: List[Card]


class DeckBase(Base):
    name: str
    description: Optional[str] = None


class DeckCreate(DeckBase):
    pass


class Deck(DeckBase):
    id: PositiveInt
    cards: Optional[List[Card]]


class Decks(Base):
    items: List[Deck]
