from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from settings.config import AppSettings

class AdminAuthenticationBackend(AuthenticationBackend):
    def __init__(self, settings: AppSettings):
        self.settings = settings

    @property
    def middlewares(self) -> list:
        return [
            Middleware(
                SessionMiddleware,
                secret_key="your-secret-key-here-change-it",
                max_age=3600,
            )
        ]

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        # Check against settings
        if username == self.settings.ADMIN_USERNAME and password == self.settings.ADMIN_PASSWORD:
            request.session.update({"user_id": 1})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        # Check if user is authenticated
        return "user_id" in request.session
