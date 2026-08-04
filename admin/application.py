
from authentication import AdminAuthenticationBackend  # Fixed import
from app.admin.views import UserAdmin  # This file doesn't exist yet
from app.infra.postgres.base import Base
from app.infra.postgres.db import Database
from settings.config import AppSettings
from sqladmin import Admin
from starlette.applications import Starlette

class AdminApplication:
    def __init__(self, app_settings: AppSettings):
        self.web_app = Starlette()
        self.database = Database(app_settings.POSTGRES_DSN, declarative_base=Base)
        self.admin = Admin(
            self.web_app,
            self.database.engine,
            authentication_backend=AdminAuthenticationBackend(settings=app_settings),
            base_url="/"
        )
        self._register_views()

    def _register_views(self) -> None:
        self.admin.add_view(UserAdmin)

def create_app() -> Starlette:
    app = AdminApplication(AppSettings())
    return app.web_app

# Add this to run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("view:create_app", host="127.0.0.1", port=8000, reload=True)
