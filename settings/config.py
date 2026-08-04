from pydantic_settings import BaseSettings
from typing import Optional

class AppSettings(BaseSettings):
    POSTGRES_DSN: str = "postgresql+asyncpg://user:password@localhost:5432/dbname"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "telegram_bot"
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = AppSettings()
