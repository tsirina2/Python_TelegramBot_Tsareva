import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def create_tables():
    dsn = "postgresql+asyncpg://tsirina:Twe2%3F0op@localhost:5432/ice_cream_db"
    
    engine = create_async_engine(dsn, echo=True)
    
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id INTEGER,
                username VARCHAR(255),
                full_name VARCHAR(255),
                is_waiter BOOLEAN DEFAULT FALSE,
                is_manager BOOLEAN DEFAULT FALSE,
                is_admin BOOLEAN DEFAULT FALSE
            )
        """))
        print("Users table created successfully!")
    
    await engine.dispose()

asyncio.run(create_tables())
