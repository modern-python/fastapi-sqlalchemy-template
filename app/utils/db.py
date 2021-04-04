from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def transaction(session: AsyncSession) -> AsyncGenerator[None, None]:
    """hack to migrate from the sub transaction pattern
    https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#migrating-from-the-subtransaction-pattern
    """
    if not session.in_transaction():
        async with session.begin():
            yield
    else:
        yield
