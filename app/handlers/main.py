import logging


from telegram.ext import Application as PTBApplication, CommandHandler
from telegram import Update
from app.handlers.commands import start
from config import get_app_settings
from app.core.users.repositories import UserService, UserRepository
from app.core.users.services import UserService
from app.infra.postgres.db import  Database


def configure_logging() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )


logging.getLogger("httpx").setLevel(logging.WARNING)


class Application:

    def __init__(self, app_settings: AppSettings):
        self._settings = app_settings
        self.ptb_application = (
            PTBApplication.builder()
            .token(self._settings.TELEGRAM_API_KEY.get_secret_value())
            .build()
        )
        self._register_handlers()
        self.database = Database(app_settings.POSTGRES_DSN)


        user_repository = UserRepository(database=self.database)
        self.user_service = UserService(repository=user_repository)
        

    def _register_handlers(self):
            handler_list = [

                CommandHandler(command="start", callback=start),
            ]

            for handler_item in handler_list:
                self.ptb_application.add_handler(handler_item)
                logging.debug(f"Handler '{type(handler_item).__name__}' registered.")

    @staticmethod
    async def initialize_depenencies(application: "Application") ->None:
        await application.database.initialize()


    @staticmethod
    async def shutdown_dependencies(apllication:"Application") ->None:
        await application.database.shutdown()

    def run(self) -> None:
            logging.info("Starting bot polling...")

            self.ptb_application.run_polling(allowed_updates=Update.ALL_TYPES)
            logging.info("Bot stopped")


    def create_app(app_settings: AppSettings) -> Application:
                application = Application(app_settings)
                .post_init(Application.initialize_dependencies)
                .post_shutdown(Application.shutdown_dependencies)
                .token(app_settings.TELEGRAM_API_KEY.get_secret_value()).build()
    return application

    if __name__ == "__main__":
        configure_logging()
        logging.info("Application starting up.")

    try:
        app_settings = get_app_settings()
        bot_app = create_app(app_settings)
        bot_app.run()

    except Exception as e:
            logging.exception("Application crashed)")

