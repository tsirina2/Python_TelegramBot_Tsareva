from app.infra.postgres.db import Database

async def create_users_table(db: Database) -> None:
    async with db.connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                is_waiter BOOLEAN DEFAULT FALSE
            );
        """)
        print("Table 'users' created successfully!")

async def add_user_id_to_events(db: Database) -> None:
    async with db.connection() as conn:
        # Add the user_id column if it doesn't exist
        await conn.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='events' AND column_name='user_id'
                ) THEN
                    ALTER TABLE events
                    ADD COLUMN user_id BIGINT;
                END IF;
            END
            $$;
        """)
        print("Column 'user_id' added to 'events' table successfully!")
