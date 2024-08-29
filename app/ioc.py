from that_depends import BaseContainer, providers

from app import repositories
from app.resources.db import create_sa_engine, create_session
from app.settings import Settings


class IOCContainer(BaseContainer):
    settings = providers.Singleton(Settings)

    database_engine = providers.Resource(create_sa_engine, settings=settings.cast)
    session = providers.ContextResource(create_session, engine=database_engine.cast)

    decks_service = providers.Factory(repositories.DecksService, session=session)
    cards_service = providers.Factory(repositories.CardsService, session=session)
