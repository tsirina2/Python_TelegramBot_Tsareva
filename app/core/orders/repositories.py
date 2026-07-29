

from dataclasses import dataclass
from sqlalchemy import select, and_, update  # ← ADD THIS IMPORT
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import insert

from app.core.orders.constants import OrderStatusEnum
from app.core.orders.models import Product, Order, OrderProduct
from app.infra.postgres.db import Database


@dataclass
class ProductRepository:
    database: Database

    async def list_products(self) -> list[Product]:
        async with self.database.session() as session:
            query = select(Product)
            return list(await session.scalars(query))


class OrderRepository:
    database: Database

    async def create_order(self, user_id: int) -> int:
        async with self.database.session() as session:
            insert_stmt = insert(Order).values(user_id=user_id, status=OrderStatusEnum.unlisted)
            result = await session.execute(insert_stmt)
            await session.commit()
            return result.scalar()  # ← FIXED

    async def get_order_by_id(self, order_id: int) -> Order | None:
        async with self.database.session() as session:
            query = select(Order).where(Order.id == order_id).options(
                joinedload(Order.products).joinedload(OrderProduct.product)  # ← FIXED
            )
            return await session.scalar(query)

    async def get_active_order_for_user(self, user_id: int) -> Order | None:  # ← FIXED: self
        async with self.database.session() as session:
            select_stmt = select(Order).where(
                and_(  # ← FIXED: and_ is now imported
                    Order.user_id == user_id,
                    Order.status.in_([OrderStatusEnum.unlisted, OrderStatusEnum.ordered])  # ← FIXED
                )
            ).options(
                joinedload(Order.products).joinedload(OrderProduct.product)  # ← FIXED
            )
            return await session.scalar(select_stmt)

    async def add_product_to_order(self, order_id: int, product_id: int) -> None:
        async with self.database.session() as session:  # ← FIXED: space after as
            insert_stmt = insert(OrderProduct).values(  # ← FIXED: insert_stmt not insert()_stmt
                order_id=order_id,
                product_id=product_id,
                amount=1
            )
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=[OrderProduct.order_id, OrderProduct.product_id],  # ← FIXED
                set_={"amount": OrderProduct.amount + 1}  # ← FIXED
            )
            await session.execute(upsert_stmt)  # ← ADDED: execute the upsert
            await session.commit()

    async def set_order_status(self, order_id: int, status: OrderStatusEnum) -> None:
        async with self.database.session() as session:
            update_stmt = update(Order).where(Order.id == order_id).values(status=status)  # ← FIXED
            await session.execute(update_stmt)
            await session.commit()