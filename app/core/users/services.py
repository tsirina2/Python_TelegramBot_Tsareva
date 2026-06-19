from dataclasses import dataclass

from app.core.users.constants import RolesEnum
from app.core.users.repositories import UserRepository


@dataclass
class UserService:
    repository: UserRepository

    async def register_visitor(self, user_id: int) -> None:
        await self.repository.create_user_if_not_exist(user_id)

    async def get_user_id_for_role(self, role: str) -> int | None:
        """Возвращает ID пользователя по роли. Пока только для роли 'waiter'."""
        if role == "waiter":
            waiter_ids = await self.repository.get_waiter_ids()
            return waiter_ids[0] if waiter_ids else None
        return None  # для других ролей — пока не поддерживается






