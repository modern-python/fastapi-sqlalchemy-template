import typing
import uuid

import pytest
from advanced_alchemy.exceptions import RepositoryError
from fastapi import status

from app import ioc
from app.resources.db import create_sa_engine
from app.settings import Settings
from tests import factories


if typing.TYPE_CHECKING:
    import modern_di
    from httpx import AsyncClient


@pytest.mark.parametrize(
    "request_kwargs",
    [
        {"method": "get", "url": "/api/decks/1/"},
        {"method": "post", "url": "/api/decks/", "json": {"name": "pool", "idempotency_key": str(uuid.uuid4())}},
    ],
)
async def test_exhausted_pool_returns_503(
    client: AsyncClient,
    di_container: modern_di.Container,
    request_kwargs: dict[str, typing.Any],
) -> None:
    pool_settings: typing.Final = Settings(db_pool_size=1, db_max_overflow=0, db_pool_timeout=0.1)
    engine: typing.Final = create_sa_engine(settings=pool_settings, url=pool_settings.db_dsn_parsed)
    di_container.override(ioc.Database.dynamic_engine, engine)
    try:
        async with engine.connect():
            response = await client.request(**request_kwargs)
    finally:
        di_container.reset_override(ioc.Database.dynamic_engine)
        await engine.dispose()

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.usefixtures("set_async_session_in_base_sqlalchemy_factory")
async def test_other_repository_errors_are_not_turned_into_503(client: AsyncClient) -> None:
    deck: typing.Final = await factories.DeckModelFactory.create_async()

    with pytest.raises(RepositoryError):
        await client.post(f"/api/decks/{deck.id}/cards/", json=[{"front": "nul \x00 byte"}])
