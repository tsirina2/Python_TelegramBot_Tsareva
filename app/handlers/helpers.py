# app/handlers/helpers.py

from dataclasses import dataclass
from enum import Enum
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from app.core.orders.constants import OrderStatusEnum


# ============================================
# FILTER HELPER FUNCTION (ADDED)
# ============================================

def filter_for_command(command_name: str) -> str:
    """
    Create a pattern for callback query filtering.
    Example: filter_for_command("add_item") returns "^add_item$"
    """
    return f"^{command_name}$"


# ============================================
# ENUMS
# ============================================

class RolesEnum(Enum):
    WAITER = "waiter"
    USER = "user"
    ADMIN = "admin"


# ============================================
# HELPER FUNCTIONS
# ============================================

def build_order_buttons(products: list) -> InlineKeyboardMarkup:
    """Build inline keyboard buttons for ordering"""
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product.name} - ${product.price}",
                callback_data=f"add_product_{product.id}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(text="✅ Submit Order", callback_data="submit_order")
    ])
    return InlineKeyboardMarkup(keyboard)


def format_order_constants(order) -> str:
    """Format order status and details"""
    if order is None:
        return "У вас нет активного заказа."

    status_map = {
        OrderStatusEnum.unlisted: "📝 Черновик",
        OrderStatusEnum.ordered: "📋 Заказан",
        OrderStatusEnum.DONE: "✅ Готов"
    }

    status_text = status_map.get(order.status, "❓ Неизвестный статус")
    return f"Заказ #{order.id}\nСтатус: {status_text}"


def format_order_contents_for_waiter(order) -> str:
    """Format order details for waiter view"""
    if order is None:
        return "Нет заказа."

    items = []
    total = 0

    for order_product in order.products:
        product = order_product.product
        amount = order_product.amount
        price = product.price * amount
        total += price
        items.append(f"- {product.name} x{amount} = ${price:.2f}")

    items_text = "\n".join(items)
    return f"📋 Заказ #{order.id}\n\n{items_text}\n\n💰 Итого: ${total:.2f}"


# ============================================
# HANDLER FUNCTIONS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    if update.effective_user and update.effective_chat:
        try:
            await context.application.user_service.register_visitor(update.effective_user.id)
            keyboard = [
                [InlineKeyboardButton(text="Sdelat zakaz", callback_data="order_create")],
                [InlineKeyboardButton(text="Завершить заказ", callback_data="complete_order")],
            ]
            markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Dobro pojalovat",
                reply_markup=markup
            )

            await update.message.reply_text("Добро пожаловать!")
        except Exception as e:
            print(f"Ошибка регистрации посетителя: {e}")
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


async def waiter_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Waiter start command handler"""
    if update.effective_chat and update.effective_user:
        try:
            await context.application.user_service.register_visitor(update.effective_user.id)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Добро пожаловать на работу!"
            )
            await update.message.reply_text("Welcome! Use /create_event to add events.")
        except Exception as e:
            print(f"Ошибка в waiter_start: {e}")
            await update.message.reply_text("Произошла ошибка.")


async def create_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create order handler"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🆕 Creating new order...")
    # Your code here


async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add item to order handler"""
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    order_service = context.application.order_service
    product_service = context.application.product_service

    parts = callback_data.split('_')
    order_id = int(parts[1])
    item_id = int(parts[2])

    products = await product_service.list_products()
    await order_service.add_product_to_order(order_id, item_id)
    order = await order_service.get_order_by_id(order_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=format_order_contents_for_waiter(order),
        reply_markup=build_order_buttons(products),
        parse_mode=ParseMode.HTML
    )


async def finish_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Finish order handler"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Order finished!")


async def waiter_finish_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Waiter finish order handler"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Waiter finished order!")


# ============================================
# HANDLER CLASS
# ============================================

@dataclass
class Handler:
    handler: CommandHandler | CallbackQueryHandler
    role: RolesEnum | None = None


# ============================================
# HANDLER REGISTRATIONS
# ============================================

HANDLERS: tuple[Handler, ...] = (
    Handler(handler=CommandHandler("start", waiter_start), role=RolesEnum.WAITER),
    Handler(handler=CommandHandler("start", start)),
    Handler(handler=CallbackQueryHandler(create_order, pattern=filter_for_command("add_item"))),
    Handler(handler=CallbackQueryHandler(add_item, pattern=filter_for_command("add_item"))),
    Handler(handler=CallbackQueryHandler(finish_order, pattern=filter_for_command("finish_order"))),
    Handler(handler=CallbackQueryHandler(waiter_finish_order, pattern=filter_for_command("waiter_finish_order")), role=RolesEnum.WAITER),
)