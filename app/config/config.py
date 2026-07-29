from pathlib import Path
from typing import Optional
from urllib.parse import quote

from pydantic import SecretStr, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

print("CONFIG FILE:", Path(__file__))
print("ENV PATH:", Path(__file__).parent / "settings" / ".env")
print("ENV EXISTS:", (Path(__file__).parent / "settings" / ".env").exists())

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / "settings" / ".env",
        extra="ignore"
    )

    # Telegram
    TELEGRAM_API_KEY: SecretStr
    LOG_LEVEL: str = "INFO"

    # Database type
    DATABASE_TYPE: str = "postgres"

    # PostgreSQL (каждый параметр отдельно, как у вас и было)
    POSTGRES_USER: str = "tsirina"
    POSTGRES_PASSWORD: SecretStr = SecretStr("Twe2?0op")
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "ice_cream_db"

    # ADMIN (добавлено по аналогии с новым файлом)
    ADMIN_INTERFACE_PORT: int = 8001
    ADMIN_SECRET_KEY: SecretStr = SecretStr("secretkey")
    ADMIN_LOGIN: SecretStr = SecretStr("admin")
    ADMIN_PASSWORD: SecretStr = SecretStr("admin")

    @property
    def postgres_dsn(self) -> PostgresDsn:
        """
        Возвращает DSN как PostgresDsn (с валидацией).
        Используем Secret для безопасного хранения.
        """
        password = quote(self.POSTGRES_PASSWORD.get_secret_value())
        dsn_str = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{password}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        # Pydantic автоматически провалидирует, что это правильный DSN
        return PostgresDsn(dsn_str)

    @property
    def database_dsn(self) -> str:
        """
        Возвращает DSN в зависимости от DATABASE_TYPE.
        Для SQLite — строка, для PostgreSQL — результат postgres_dsn.
        """
        if self.DATABASE_TYPE == "sqlite":
            return "sqlite+aiosqlite:///./ice_cream.db"
        return str(self.postgres_dsn)
