from dataclasses import dataclass

from app.core.users.repositories import UserRepository
from app.core.users.repositories import UserRepository

class UserService:
    def __init__(self, repository: UserRepository, db):
        """
        repository: UserRepository instance, for user registration
        db: Database instance, for storing user state
        """
        self.repository = repository
        self.db = db

    # ----------------------------
    # Register visitor
    # ----------------------------
    async def register_visitor(self, user_id: int) -> None:
        await self.repository.create_user_if_not_exists(user_id)

    # ----------------------------
    # Track user state
    # ----------------------------
    async def set_user_state(self, user_id: int, state: str):
        async with self.db.connection() as conn:
            await conn.execute(
                "UPDATE users SET state = $1 WHERE id = $2",
                state,
                user_id
            )

    async def get_user_state(self, user_id: int) -> str:
        async with self.db.connection() as conn:
            row = await conn.fetchrow(
                "SELECT state FROM users WHERE id = $1",
                user_id
            )
            return row["state"] if row else "idle"

