import typing

import pytest
from sqlalchemy import Engine, create_engine

from app.settings import settings


@pytest.fixture
def alembic_engine() -> typing.Iterator[Engine]:
    # Replaces pytest-alembic's default in-memory SQLite engine.
    engine: typing.Final = create_engine(settings.db_dsn_parsed.set(drivername="postgresql+psycopg"))
    yield engine
    engine.dispose()
