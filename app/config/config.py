from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote


class AppSettings(BaseSettings):
    # Load .env from the correct folder
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / "settings" / ".env"
    )

    # Telegram configuration
    TELEGRAM_API_KEY: SecretStr
    LOG_LEVEL: str = "INFO"

    # PostgreSQL configuration
    POSTGRES_USER: str = "tsirina"
    POSTGRES_PASSWORD: SecretStr = SecretStr("Twe2?0op")
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "ice_cream_db"

    @property
    def POSTGRES_DSN(self) -> str:
        """
        Returns PostgreSQL DSN as a plain string suitable for asyncpg.
        Special characters in password are URL-encoded automatically.
        """
        password = quote(self.POSTGRES_PASSWORD.get_secret_value())  # encode special chars
        return f"postgresql://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"




