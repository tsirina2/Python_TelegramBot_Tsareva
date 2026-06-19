from dataclasses import dataclass
from sqlalchemy import insert, select
from app.infra.postgres.db import Database
from app.core.users.models import User


@dataclass
class UserRepository:
    database: Database

    async def create_user_if_not_exists(self, user_id: int, is_waiter: bool = False) -> None:
        async with self.database.session() as session:
            insert_stmt = (
                insert(User)
                .values(id=user_id, is_waiter=is_waiter)
                .on_conflict_do_nothing(index_elements=['id'])
            )
            await session.execute(insert_stmt)
            await session.commit()

    async def get_waiter_ids(self) -> list[int]:
        """Возвращает список ID всех пользователей с ролью официанта."""
        async with self.database.session() as session:
            result = await session.execute(select(User.id).where(User.is_waiter == True))
            rows = result.scalars().all()
            return list(rows)
