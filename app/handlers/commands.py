from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler
from app.core.orders.constants import OrderStatusEnum
from app.core.orders.exceptions import ActiveOrderExists
from app.core.orders.services import ProductService, OrderService
from app.core.orders.services import OrderService
from app.handlers.helpers import (
    build_order_buttons,
    format_order_constants,
    format_order_contents_for_waiter,
)


# ... (ALL YOUR EXISTING FUNCTIONS: start, waiter_start, register,
#      handle_user_message, create_event_start, complete_order, create_order)


# ============ ADD ITEM HANDLER - FIXED ============

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for adding items to an existing order.
    Callback data format: "add_{order_id}_{item_id}"
    """
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    order_service: OrderService = context.application.order_service
    product_service: ProductService = context.application.product_service

    # FIXED #1: Use split() to parse callback data
    parts = callback_data.split('_')
    order_id = int(parts[1])
    item_id = int(parts[2])

    products = await product_service.list_products()

    await order_service.add_product_to_order(order_id, item_id)
    order = await order_service.get_order_by_id(order_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=format_order_contents_for_waiter(order),  # FIXED #2: Now imported
        reply_markup=build_order_buttons(order_id, products),
        parse_mode=ParseMode.f
    )


async def complete_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Complete order handler"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Order completed!")
    # Add your logic here


async def create_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create order handler"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🆕 Creating new order...")
    # Add your logic here


# ============ HANDLER REGISTRATION - FIXED ============

async def register_handlers(application):
    """
    Register all handlers for the bot.
    """
    # Add the complete order callback handler
    application.add_handler(CallbackQueryHandler(complete_order, pattern="^complete_order$"))

    # Add the create order callback handler
    application.add_handler(CallbackQueryHandler(create_order, pattern="^order_create$"))

    # FIXED #4: ADD THE add_item HANDLER
    application.add_handler(CallbackQueryHandler(add_item, pattern="^add_"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome!"
    )


async def waiter_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Waiter mode started!"
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Registration is not implemented yet.")


async def create_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Event creation started.")


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(f"You said: {update.message.text}")