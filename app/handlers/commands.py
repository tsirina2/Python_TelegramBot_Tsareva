from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler, filters

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await context.application.user_service.register_visitor(user_id)
    await update.message.reply_text("Welcome! Use /create_event to add events.")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    created = await context.application.user_service.register_user(user_id)
    text = "✅ Registered!" if created else "ℹ️ Already registered."
    await update.message.reply_text(text)

# Other handlers like create_event_start and handle_user_message




async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    state = await context.application.user_service.get_user_state(user_id)

    if state == "creating_event":
        event = context.application.user_event_data[user_id]

        if event["name"] is None:
            event["name"] = text
            await update.message.reply_text("Got it! Now send the event date (YYYY-MM-DD):")
            return
        if event["date"] is None:
            event["date"] = text
            await update.message.reply_text("Send the event time (HH:MM):")
            return
        if event["time"] is None:
            event["time"] = text
            await update.message.reply_text("Finally, send event details or '-' for none:")
            return
        if event["details"] is None:
            event["details"] = text if text != "-" else ""

            # Save to database
            event_id = await context.application.calendar.create_event(
                event["name"], event["date"], event["time"], event["details"], user_id
            )

            await update.message.reply_text(f"Event '{event['name']}' created! (ID: {event_id})")

            # Reset state
            await context.application.user_service.set_user_state(user_id, "idle")
            context.application.user_event_data.pop(user_id)
            return

    else:
        await update.message.reply_text("Please start with /create_event to add a new event.")

async def create_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.effective_chat:
        return

    user_id = update.effective_user.id

    # Register visitor if not already
    await context.application.user_service.register_visitor(user_id)

    # Set user state to creating_event
    await context.application.user_service.set_user_state(user_id, "creating_event")

    # Initialize temporary storage for this user's event
    if not hasattr(context.application, "user_event_data"):
        context.application.user_event_data = {}
    context.application.user_event_data[user_id] = {
        "name": None,
        "date": None,
        "time": None,
        "details": None,
    }

    await update.message.reply_text(
        "Let's create a new event! Please send the event name."
    )

