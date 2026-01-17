from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from app import models


class DecksRepository(SQLAlchemyAsyncRepositoryService[models.Deck]):
    class BaseRepository(SQLAlchemyAsyncRepository[models.Deck]):
        model_type = models.Deck

    repository_type = BaseRepository


class CardsRepository(SQLAlchemyAsyncRepositoryService[models.Card]):
    class BaseRepository(SQLAlchemyAsyncRepository[models.Card]):
        model_type = models.Card

    repository_type = BaseRepository
