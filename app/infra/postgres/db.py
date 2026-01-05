import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from pydantic import PostgresDsn


class Database:
    def __init__(self, dsn: PostgresDsn):
        self._dsn = dsn
        self._pool: asyncpg.Pool | None = None

    async def initialize(self) -> None:
        self._pool = await asyncpg.create_pool(
            dsn=str(self._dsn)
        )

    async def shutdown(self) -> None:
        if self._pool is None:
            raise RuntimeError("Connection pool has not been created")

        await self._pool.close()

    @asynccontextmanager
    async def connection(
            self,
    ) -> AsyncGenerator[asyncpg.pool.PoolConnectionProxy, None]:
        if self._pool is None:
            raise RuntimeError("Connection pool has not been created")

        async with self._pool.acquire() as connection:
            yield connection


