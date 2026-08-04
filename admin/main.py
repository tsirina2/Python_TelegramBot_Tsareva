import uvicorn
from .authentification import AdminAuthenticationBackend
from fastapi import FastAPI
from sqladmin import Admin
from app.infra.postgres.base import Base
from app.infra.postgres.db import Database
from settings.config import AppSettings

class AdminApplication:
    def __init__(self, app_settings: AppSettings):
        self.settings = app_settings
        self.web_app = FastAPI()
        self.database = Database(self.settings.POSTGRES_DSN, declarative_base=Base)
        self.auth_backend = AdminAuthenticationBackend(self.settings)
        self.admin = Admin(
            self.web_app,
            self.database.engine,
            authentication_backend=self.auth_backend,
            base_url="/"
        )

def create_app():
    app_settings = AppSettings()
    admin_app = AdminApplication(app_settings)
    return admin_app.web_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "admin.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )
