
from app.infra.postgres.db import Database

class Calendar:
    def __init__(self, db: Database):
        self.db = db

    # ------------------------
    # CREATE
    # ------------------------
    async def create_event(self, event_name: str, event_date: str, event_time: str, event_details: str):
        async with self.db.connection() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO events(name, date, time)
                VALUES($1, $2, $3)
                RETURNING id
                """,
                event_name,
                event_date,
                event_time
            )
            event_id = result["id"]
        return event_id

    # ------------------------
    # READ a single event by name
    # ------------------------
    async def read_event(self, event_name: str):
        async with self.db.connection() as conn:
            event = await conn.fetchrow(
                "SELECT * FROM events WHERE name = $1",
                event_name
            )
        return dict(event) if event else None

    # ------------------------
    # DISPLAY all events
    # ------------------------
    async def display_events(self,user_it:int):
        async with self.db.connection() as conn:
            events = await conn.fetch("SELECT * FROM events ORDER BY date, time")
        return [dict(e) for e in events]

    # ------------------------
    # EDIT an event
    # ------------------------
    async def edit_event(self, event_name: str, new_date: str = None, new_time: str = None, new_details: str = None):
        # Build dynamic query
        updates = []
        values = []
        if new_date:
            updates.append("date = $%d" % (len(values) + 1))
            values.append(new_date)
        if new_time:
            updates.append("time = $%d" % (len(values) + 1))
            values.append(new_time)
        if new_details:
            updates.append("details = $%d" % (len(values) + 1))
            values.append(new_details)

        if not updates:
            return False  # nothing to update

        values.append(event_name)
        query = f"UPDATE events SET {', '.join(updates)} WHERE name = ${len(values)}"

        async with self.db.connection() as conn:
            result = await conn.execute(query, *values)
        return result  # returns asyncpg status string like "UPDATE 1"

    # ------------------------
    # DELETE an event
    # ------------------------
    async def delete_event(self, event_name: str):
        async with self.db.connection() as conn:
            result = await conn.execute("DELETE FROM events WHERE name = $1", event_name)
        return result  # returns asyncpg status string like "DELETE 1"
