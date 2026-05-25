from dataclasses import dataclass
from telegram.ext import BaseHandler, CommandHandler, Application
from app.core.users.constants import RolesEnum
from app.handlers.commands import start, waiter_start

@dataclass
class Handler:
    handler: BaseHandler
    role: RolesEnum | None = None

    def attach_to_application(self, application: Application):
        self.handler.callback_data = {'required_role': self.role}
        application.add_handler(self.handler)

HANDLERS: tuple[Handler, ...] = (
    Handler(
        handler=CommandHandler(command="start", callback=waiter_start),
        role=RolesEnum.waiter
    ),
    Handler(
        handler=CommandHandler(command="start_user", callback=start)
    ),
)

def setup_handlers(application: Application) -> None:
    """Добавляет все обработчики из HANDLERS в приложение."""
    for handler_config in HANDLERS:
        handler_config.attach_to_application(application)



