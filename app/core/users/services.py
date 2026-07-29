from dataclasses import dataclass
from typing import Optional

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from app.core.users.constants import RolesEnum
from app.core.users.repositories import UserRepository
from app.core.orders.services import OrderService


# Add this function if it doesn't exist elsewhere
def format_order_contents_for_waiter(order) -> str:
    """Format order details for waiter display."""
    # Example implementation - adjust based on your Order model
    items = getattr(order, 'items', [])
    items_text = "\n".join([f"- {item}" for item in items])
    return f"Order #{order.id}\nItems:\n{items_text}"


@dataclass
class UserService:
    repository: UserRepository

    async def register_visitor(self, user_id: int) -> None:
        await self.repository.create_user_if_not_exist(user_id)

    async def get_user_id_for_role(self, role: str) -> int | None:
        if role == "waiter":
            waiter_ids = await self.repository.get_waiter_ids()
            return waiter_ids[0] if waiter_ids else None
        return None

    async def get_waiter_user_ids(self) -> list[int]:
        """Get all waiter user IDs."""
        return await self.repository.get_waiter_ids()


async def finish_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle waiter finishing an order."""
    query = update.callback_query
    await query.answer()

    # Guard against None values
    if not query or not update.effective_chat:
        return

    callback_data = query.data
    order_service: OrderService = context.application.order_service
    user_service: UserService = context.application.user_service

    # Extract order ID from callback data (e.g., "waiter_finish_order_123")
    try:
        order_id = int(callback_data.split('_')[-1])
    except (ValueError, IndexError):
        await query.edit_message_text("Invalid order ID!")
        return

    await order_service.send_order_to_waiters(order_id)

    # Send confirmation to the user
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Zakaz byl peredan nashim ofiziantam, pjidayte v blijajshee vremya!"
    )

    # Notify all waiters
    waiter_users_ids = await user_service.get_waiter_user_ids()
    order = await order_service.get_order_by_id(order_id)

    for waiter_id in waiter_users_ids:
        await context.bot.send_message(
            chat_id=waiter_id,
            text=f"Sozdan novy zakaz: {order_id}\n\n"
                 f"{format_order_contents_for_waiter(order)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="Zakaz dostavlen",
                    callback_data=f"waiter_finish_order_{order_id}"
                )]
            ])
        )









