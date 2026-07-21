from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from settings.config import AppSettings

class AdminAuthenticationBackend(AuthenticationBackend):
    def _init__(self, settings:AppSettings):
        self.settings = settings

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        return username == "admin" and password == "admin"

    async def logout(self, request: Request) -> bool:
        return True

    async def authenticate(self,request:Request):
        return None
