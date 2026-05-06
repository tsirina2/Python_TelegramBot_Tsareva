

from pathlib import Path
from urllib.parse import quote

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / "settings" / ".env"
    )

    # Telegram
    TELEGRAM_API_KEY: SecretStr
    LOG_LEVEL: str = "INFO"

    # PostgreSQL
    POSTGRES_USER: str = "tsirina"
    POSTGRES_PASSWORD: SecretStr = SecretStr("Twe2?0op")
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "ice_cream_db"

    @property
    def postgres_dsn(self) -> str:
        """Return PostgreSQL DSN string for asyncpg."""
        password = quote(self.POSTGRES_PASSWORD.get_secret_value())

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{password}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


