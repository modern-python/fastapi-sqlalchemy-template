from that_depends import BaseContainer, providers

from app.db.resource import create_sa_engine, create_session
from app.repositories.decks import CardsRepository, DecksRepository
from app.settings import Settings


class IOCContainer(BaseContainer):
    settings = providers.Singleton(Settings)

    database_engine = providers.AsyncResource(create_sa_engine, settings=settings.cast)
    session = providers.AsyncContextResource(create_session, engine=database_engine.cast)

    decks_repo = providers.Factory(DecksRepository, session=session)
    cards_repo = providers.Factory(CardsRepository, session=session)
