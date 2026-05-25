import logging
import asyncio

from sqlalchemy.orm import declarative_base
from ptbcontrib.roles import RolesHandler
from telegram.ext import Application as PTBApplication, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.commands import start, register, create_event_start, handle_user_message
from app.config.config import AppSettings
from app.core.users.repositories import UserRepository
from app.core.users.services import UserService
from app.infra.postgres.db import Database
from app.core.my_calendar import Calendar
from app.core.users.constants import RolesEnum

Base = declarative_base()

class Application:
    def __init__(self, app_settings: AppSettings, **kwargs):
        self.app_settings = app_settings
        self._roles_handler = None  # Храним один экземпляр RolesHandler

        # Инициализация БД
        self.database = Database(
            self.app_settings.postgres_dsn,
            declarative_base=Base
        )

        # Создание календаря
        self.calendar = Calendar(self.database)

        # Создание репозитория и сервиса пользователей
        user_repository = UserRepository(database=self.database)
        self.user_service = UserService(repository=user_repository)

        # Создание приложения бота БЕЗ post_init/post_shutdown
        self.bot_app = (
            PTBApplication.builder()
            .token(self.app_settings.TELEGRAM_API_KEY.get_secret_value())
            .build()
        )

        # Явная инициализация зависимостей ДО запуска бота
        asyncio.run(self.initialize_dependencies(self.bot_app))

        # Регистрация обработчиков — ПОСЛЕ всех инициализаций
        self._register_handlers()

    async def initialize_dependencies(self, app: PTBApplication) -> None:
        """Инициализирует зависимости приложения (БД и т. д.)."""
        try:
            logging.info("Initializing database...")
            await self.database.initialize()
            logging.info("Database initialized successfully")

            # Добавляем инициализацию ролей
            logging.info("Setting up roles...")
            await self.setup_roles()
            logging.info("Roles setup completed")
        except Exception as e:
            logging.error(f"Failed to initialize dependencies: {e}")
            raise

    async def shutdown_dependencies(self) -> None:
        """Завершает работу зависимостей (закрывает соединения с БД)."""
        try:
            logging.info("Shutting down database...")
            await self.database.shutdown()
            logging.info("Database shutdown completed")
        except Exception as e:
            logging.error(f"Failed to shutdown database: {e}")

    def _register_handlers(self) -> None:
        handlers = [
            CommandHandler("start", start),
            CommandHandler("register", register),
            CommandHandler("create_event", self.event_create_handler),
        ]

        self.bot_app.add_error_handler(self._error_handler)

        for handler in handlers:
            self.bot_app.add_handler(handler)

        self.bot_app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message)
        )

    async def _error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.error("Exception while handling update:", exc_info=context.error)

    async def setup_roles(self) -> None:
        """Инициализирует роли для бота."""
        try:
            # Создаём один RolesHandler для всех ролей
            self._roles_handler = RolesHandler(roles=[role.value for role in RolesEnum])
            # Получаем всех пользователей для каждой роли и добавляем их
            for role in RolesEnum:
                user_ids = await self.user_service.get_user_ids_for_role(role.value)
                for user_id in user_ids:
                    self._roles_handler.add_member(user_id, role=role.value)

            logging.info(f"Roles initialized: {list(self._roles_handler.roles.keys())}")
        except Exception as e:
            logging.error(f"Failed to setup roles: {e}")
            raise

    async def event_create_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            event_name = update.message.text[14:]
            event_date = "2023-03-14"
            event_time = "14:00"
            event_details = "Описание события"
            user_id = update.effective_user.id
            event_id = await self.calendar.create_event(
                event_name, event_date, event_time, event_details, user_id
            )

            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"Событие {event_name} создано и имеет номер {event_id}."
            )
        except Exception as e:
            logging.exception(e)
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="При создании события произошла ошибка."
            )

    async def run(self) -> None:
        logging.info("Starting bot polling...")
        try:
            await self.bot_app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                poll_interval=2.0,
                drop_pending_updates=False
            )
        except Exception as e:
            logging.error(f"Error in bot polling: {e}")
            raise

def configure_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

if __name__ == "__main__":
    configure_logging()
    logging.info("Application starting up.")

    # Создаём экземпляр приложения
    app_settings = AppSettings()
    bot_app = Application(app_settings)

    try:
        # Запускаем бота напрямую — без ручного управления event loop
        asyncio.run(bot_app.run())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Application crashed: {e}")
    finally:
        # Корректно завершаем работу
        try:
            asyncio.run(bot_app.shutdown_dependencies())
        except:
            pass