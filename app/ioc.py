from modern_di import Group, Scope, providers

from app.repositories import CardsRepository, DecksRepository
from app.resources.db import close_sa_engine, close_session, create_sa_engine, create_session


class Dependencies(Group):
    database_engine = providers.Factory(
        creator=create_sa_engine, cache_settings=providers.CacheSettings(finalizer=close_sa_engine)
    )
    session = providers.Factory(
        scope=Scope.REQUEST, creator=create_session, cache_settings=providers.CacheSettings(finalizer=close_session)
    )

    decks_repository = providers.Factory(
        scope=Scope.REQUEST,
        creator=DecksRepository,
        bound_type=DecksRepository,
        kwargs={"session": session, "auto_commit": True},
        skip_creator_parsing=True,
    )
    cards_repository = providers.Factory(
        scope=Scope.REQUEST,
        creator=CardsRepository,
        bound_type=CardsRepository,
        kwargs={"session": session, "auto_commit": True},
        skip_creator_parsing=True,
    )
