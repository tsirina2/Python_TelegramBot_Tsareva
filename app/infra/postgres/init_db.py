import asyncio
from app.infra.postgres.db import Database

CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL
);
"""

async def init_db() -> None:

    db = Database(dsn="postgresql://tsirina:your_password@localhost:5432/ice_cream_db")
    await db.initialize()

    async with db.connection() as conn:
        await conn.execute(CREATE_EVENTS_TABLE)

    await db.shutdown()


if __name__ == "__main__":
    asyncio.run(init_db())
