import asyncio
from app.infra.postgres.db import Database
from app.core.my_calendar import Calendar

async def main():
    # 1. Create a Database instance
    db = Database(dsn="your_connection_string_here")
    await db.initialize()

    async with db.connection() as conn:
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        print(tables)
    # 2. Create a Calendar instance
    calendar = Calendar(db)

    # 3. Example: create an event
    event_id = await calendar.create_event("Meeting", "2026-01-11", "14:00", "Discuss project")
    print("Created event with ID:", event_id)

    await db.shutdown()



