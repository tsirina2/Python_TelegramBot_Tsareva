import asyncio
from app.infra.postgres.db import Database, dsn

async def test_connection():
    db = Database(dsn)
    await db.initialize()

    async with db.connection() as conn:
        result = await conn.fetchval("SELECT 1;")
        print("DB response:", result)

    await db.shutdown()

if __name__ == "__main__":
    asyncio.run(test_connection())
