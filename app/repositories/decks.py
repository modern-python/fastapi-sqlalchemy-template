import dataclasses

from app import models
from app.repositories.base import BaseRepository


@dataclasses.dataclass(kw_only=True)
class DecksRepository(BaseRepository[models.Deck]):
    model = models.Deck


@dataclasses.dataclass(kw_only=True)
class CardsRepository(BaseRepository[models.Card]):
    model = models.Card
