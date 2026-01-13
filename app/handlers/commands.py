from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat and update.effective_user:
        user_id = update.effective_user.id  # get Telegram ID here

        # Register visitor
        await context.application.user_service.register_visitor(user_id)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Добро пожаловать!",
        )
