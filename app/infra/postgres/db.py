import asyncpg
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

load_dotenv()  # loads .env file in the project root

class Database:
    def __init__(self, dsn: str | None = None):
        # Use DSN if provided, otherwise build it from environment variables
        self._dsn = dsn or (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}"
            f"/{os.getenv('DB_NAME')}"
        )
        self._pool: asyncpg.Pool | None = None

    async def initialize(self) -> None:
        self._pool = await asyncpg.create_pool(dsn=self._dsn)
        print("Database pool initialized ✅")

    async def shutdown(self) -> None:
        if self._pool:
            await self._pool.close()
            print("Database pool closed ✅")

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        if self._pool is None:
            raise RuntimeError("Database pool not initialized")
        async with self._pool.acquire() as conn:
            yield conn


