from sqlalchemy import BOOLEAN, BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.postgres.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    is_waiter: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)

