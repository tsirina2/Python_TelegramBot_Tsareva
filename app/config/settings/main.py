import logging

from telegram.ext import Application as PTBApplication, CommandHandler
from telegram import Update

from app.handlers.commands import start
from app.config.config import AppSettings
from app.core.users.repositories import UserRepository
from app.core.users.services import UserService
from app.infra.postgres.db import Database


def configure_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


logging.getLogger("httpx").setLevel(logging.WARNING)


class Application:

    def __init__(self, app_settings: AppSettings):
        self._settings = app_settings

        self.database = Database(app_settings.POSTGRES_DSN)

        self.ptb_application = (
            PTBApplication.builder()
            .token(self._settings.TELEGRAM_API_KEY.get_secret_value())
            .post_init(self.initialize_dependencies)
            .post_shutdown(self.shutdown_dependencies)
            .build()
        )

        self._register_handlers()

        user_repository = UserRepository(database=self.database)
        self.user_service = UserService(repository=user_repository)

    def _register_handlers(self):
        handlers = [
            CommandHandler(command="start", callback=start),
        ]

        for handler in handlers:
            self.ptb_application.add_handler(handler)

    async def initialize_dependencies(self, app: PTBApplication) -> None:
        await self.database.initialize()

    async def shutdown_dependencies(self, app: PTBApplication) -> None:
        await self.database.shutdown()

    def run(self) -> None:
        logging.info("Starting bot polling...")
        self.ptb_application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    configure_logging()
    logging.info("Application starting up.")

    try:
        app_settings = AppSettings()
        bot_app = Application(app_settings)
        bot_app.run()
    except Exception:
        logging.exception("Application crashed")

