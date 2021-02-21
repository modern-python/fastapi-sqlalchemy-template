from typing import List, Optional

from pydantic import BaseModel  # pylint: disable=E0611


class Base(BaseModel):
    class Config:
        orm_mode = True


class Deck(Base):
    id: Optional[int]
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class Decks(Base):
    decks: List[Deck]
