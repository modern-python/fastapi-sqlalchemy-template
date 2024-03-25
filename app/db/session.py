from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession


Session: ContextVar[AsyncSession] = ContextVar("session")
