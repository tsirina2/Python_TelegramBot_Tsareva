import logging

from telegram.ext import Application as PTBApplication, CommandHandler
from telegram import Update

from app.handlers.commands import start,register
from app.config.config import AppSettings
from app.core.users.repositories import UserRepository
from app.core.users.services import UserService
from app.infra.postgres.db import Database
from app.core.my_calendar import Calendar
from telegram.ext import MessageHandler, filters
from app.handlers.commands import create_event_start, handle_user_message


def configure_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


logging.getLogger("httpx").setLevel(logging.WARNING)



class Application:

    def __init__(self, app_settings: AppSettings):
        self.app_settings = app_settings

        self.database = Database(str(self.app_settings.POSTGRES_DSN))

        self.calendar = Calendar(self.database)

        self.bot_app= (
            PTBApplication.builder()
            .token(self.app_settings.TELEGRAM_API_KEY.get_secret_value())
            .post_init(self.initialize_dependencies)
            .post_shutdown(self.shutdown_dependencies)
            .build()
        )

        self._register_handlers()

        user_repository = UserRepository(database=self.database)
        self.user_service = UserService(repository=user_repository, db=self.database)



    def _register_handlers(self):
        handlers = [

            CommandHandler("start", start),
            CommandHandler("register", register),
            CommandHandler("create_event", self.event_create_handler),
        ]
        for handler in handlers:
            self.bot_app.add_handler(handler)

            self.bot_app.add_handler(CommandHandler("create_event", create_event_start))
            self.bot_app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message)
        )

    async def event_create_handler(self,update,context):
            try:
                event_name =update.message.text[14:]
                event_date = "2023 - 03 -14"
                event_time = "14:00"
                event_details = "Описание события"
                user_id = update.effective_user.id
                event_id = await self.calendar.create_event(event_name, event_date, event_time, event_details)

        # Отправить пользователю подтверждение
                await context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"Событие {event_name} создано и имеет номер {event_id}.")

            except Exception as e:
                logging.exception(e)
                await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="При создании события произошла ошибка."
                  )

    async def initialize_dependencies(self, app: PTBApplication) -> None:
        await self.database.initialize()

    async def shutdown_dependencies(self, app: PTBApplication) -> None:
        await self.database.shutdown()

    def run(self) -> None:
        logging.info("Starting bot polling...")
        self.bot_app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    configure_logging()
    logging.info("Application starting up.")

    try:
        app_settings = AppSettings()
        bot_app = Application(app_settings)
        bot_app.run()
    except Exception:
        logging.exception("Application crashed")


