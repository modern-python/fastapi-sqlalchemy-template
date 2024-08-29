from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from app import models


class DecksRepository(SQLAlchemyAsyncRepository[models.Deck]):
    model_type = models.Deck


class DecksService(SQLAlchemyAsyncRepositoryService[models.Deck]):
    repository_type = DecksRepository


class CardsRepository(SQLAlchemyAsyncRepository[models.Card]):
    model_type = models.Card


class CardsService(SQLAlchemyAsyncRepositoryService[models.Card]):
    repository_type = CardsRepository
