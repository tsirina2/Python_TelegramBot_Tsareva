from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text


class Database:
    def __init__(self, dsn: str, declarative_base):
        self.engine = create_async_engine(dsn, echo=False)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.Base = declarative_base

    async def initialize(self):
        """Creates all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

    async def shutdown(self):
        """Closes database connections."""
        await self.engine.dispose()

    def session(self):
        """Returns a new session."""
        return self.session_factory()
