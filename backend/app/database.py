from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Lazy engine creation — avoids import-time errors when DB driver isn't installed (e.g. tests)
_engine = None
_async_session = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url, echo=settings.debug)
    return _engine


def _get_session_factory():
    global _async_session
    if _async_session is None:
        _async_session = async_sessionmaker(_get_engine(), expire_on_commit=False)
    return _async_session


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with _get_session_factory()() as session:
        yield session
