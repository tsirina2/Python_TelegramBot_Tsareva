from typing import AsyncGenerator
from contextlib import asynccontextmanager

from pydantic import PostgresDsn, Secret
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class Database:

    def __init__(self, dsn: str, declarative_base):
        self.engine = create_async_engine(dsn)
        self.session_factory = async_sessionmaker(self.engine)
        self.Base = declarative_base

    async def initialize(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

    async def shutdown(self):
        await self.engine.dispose()

    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(
                self._declarative_base.metadata.create_all
            )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._async_session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()