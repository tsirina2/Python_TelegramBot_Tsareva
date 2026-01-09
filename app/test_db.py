import asyncio
import asyncpg
from app.config.config import AppSettings
import traceback

async def test_connection():
    settings = AppSettings()
    dsn = str(settings.POSTGRES_DSN)
    print("Using DSN:", dsn)

    try:
        conn = await asyncpg.connect(dsn)
        val = await conn.fetchval("SELECT 1;")
        print("DB response:", val)
        await conn.close()
        print("Connection successful!")
    except Exception as e:
        print("Error inside coroutine:")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(test_connection())
    except Exception as e:
        print("Error in asyncio.run():")
        traceback.print_exc()

