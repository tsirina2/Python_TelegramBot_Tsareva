
import os
from dotenv import load_dotenv
import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pydantic import PostgresDsn

# Load environment variables once at the top
load_dotenv()

# Get DB values from .env
DB_NAME = "ice_cream_db"
DB_USER = "tsirina"
DB_PASSWORD = "Twe2?0op"
DB_HOST = "localhost"
DB_PORT = "5432"
# Build DSN for asyncpg
dsn = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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


