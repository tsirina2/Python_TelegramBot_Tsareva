from app.infra.postgres.db import Database, dsn

async def create_users_table(db: Database) -> None:
    async with db.connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                is_waiter BOOLEAN DEFAULT FALSE
            );
        """)

        print("Table 'users' created successfully!")