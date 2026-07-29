import logging
print("HELLO FROM MAIN")

import asyncio
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

# === Единый Base и модель User — внутри main.py ===
Base = declarative_base()


# 🔽 Определяем User здесь, чтобы Base.metadata его "увидел"
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    is_waiter = Column(Boolean, default=False)
    is_manager = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)


# 🔼

# === Остальные импорты — после Base ===
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


class Application:
    def __init__(self, app_settings: AppSettings, **kwargs):
        self.app_settings = app_settings
        self._roles_handler = None
        self._initialized = False

        # Инициализация БД с нашим Base (в котором уже есть User)
        self.database = Database(
            self.app_settings.database_dsn,
            declarative_base=Base
        )

        print(f"DSN: {self.app_settings.database_dsn}")

        # Создание календаря
        self.calendar = Calendar(self.database)

        # Создание репозитория и сервиса пользователей
        user_repository = UserRepository(database=self.database)
        self.user_service = UserService(repository=user_repository)

        # Создание приложения бота
        self.bot_app = (
            PTBApplication.builder()
            .token(self.app_settings.TELEGRAM_API_KEY.get_secret_value())
            .build()
        )

        # Регистрация обработчиков
        self._register_handlers()

    async def initialize_dependencies(self) -> None:
        """Инициализирует зависимости: БД и роли."""
        try:
            logging.info("Initializing database...")
            await self.database.initialize()
            logging.info("Database initialized successfully")

            logging.info("Setting up roles...")
            await self.setup_roles()
            logging.info("Roles setup completed")
            self._initialized = True
        except Exception as e:
            logging.error(f"Failed to initialize dependencies: {e}")
            raise

    async def shutdown_dependencies(self) -> None:
        """Завершает работу зависимостей."""
        try:
            logging.info("Shutting down database...")
            await self.database.shutdown()
            logging.info("Database shutdown completed")
        except Exception as e:
            logging.error(f"Failed to shutdown database: {e}")

    def _register_handlers(self) -> None:
        """Регистрирует обработчики команд и сообщений."""
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
        """Логирует ошибки."""
        logging.error("Exception while handling update:", exc_info=context.error)

    async def setup_roles(self) -> None:
        """Инициализирует систему ролей."""
        try:
            # Обёртка для совместимости с ptbcontrib.roles
            class FakeUpdater:
                def __init__(self, app):
                    self._app = app
                    self.callback = app.update_queue

            self._wrapped_app = FakeUpdater(self.bot_app)

            # Создаём и регистрируем RolesHandler
            self._roles_handler = RolesHandler(
                handler=self._wrapped_app,
                roles=[role.value for role in RolesEnum]
            )
            self.bot_app.add_handler(self._roles_handler)

            # Добавляем пользователей в роли
            for role in RolesEnum:
                user_id = await self.user_service.get_user_id_for_role(role.value)
                if user_id:
                    self._roles_handler.add_member(user_id, role=role.value)

            logging.info(f"Roles initialized: {self._roles_handler.roles}")
        except Exception as e:
            logging.error(f"Failed to setup roles: {e}")
            raise

    async def event_create_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /create_event."""
        try:
            event_name = update.message.text[14:].strip()
            if not event_name:
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text="Пожалуйста, укажите название события. Пример: /create_event Открытие фестиваля"
                )
                return

            event_date = "2023-03-14"
            event_time = "14:00"
            event_details = "Описание события"
            user_id = update.effective_user.id

            event_id = await self.calendar.create_event(
                event_name, event_date, event_time, event_details, user_id
            )

            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"Событие «{event_name}» успешно создано. Номер события: {event_id}."
            )
        except Exception as e:
            logging.exception(e)
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Произошла ошибка при создании события."
            )

    def run(self):
                asyncio.run(self._run())

    async def _run(self):
        await self.bot_app.initialize()
        await self.bot_app.start()
        await self.bot_app.updater.start_polling(
                allowed_updates=Update.ALL_TYPES
                )

        await asyncio.Event().wait()
        print("6. run_polling returned")


def configure_logging() -> None:
    """Настраивает логирование."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

  # ✅ NOTE: No await, no asyncio.run()!

if __name__ == "__main__":
    print("=== MAIN STARTED ===")

    configure_logging()

    app_settings = AppSettings()
    print("=== SETTINGS LOADED ===")

    bot_app = Application(app_settings)
    print("=== APPLICATION CREATED ===")

    bot_app.run()

    print("=== RUN RETURNED ===")