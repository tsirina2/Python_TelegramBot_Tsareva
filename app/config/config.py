from pathlib import Path

from pydantic import SecretStr, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


print("CONFIG FILE:", Path(__file__))
print(
    "ENV PATH:",
    Path(__file__).parent / "settings" / ".env"
)
print(
    "ENV EXISTS:",
    (Path(__file__).parent / "settings" / ".env").exists()
)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / "settings" / ".env",
        extra="ignore"
    )

    # Telegram
    TELEGRAM_API_KEY: SecretStr

    # Logging
    LOG_LEVEL: str = "INFO"

    # Database type
    DATABASE_TYPE: str = "postgres"

    # PostgreSQL
    POSTGRES_USER: str = "tsirina"
    POSTGRES_PASSWORD: SecretStr = SecretStr("Twe2?0op")
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "ice_cream_db"

    @computed_field
    @property
    def POSTGRES_DSN(self) -> PostgresDsn:
        return MultiHostUrl.build(

                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD.get_secret_value(),
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )


    @computed_field
    @property
    def PERSISTANCE_POSTGRES_DSN(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @property
    def database_dsn(self) -> str:
        """
        Returns DSN depending on DATABASE_TYPE.
        SQLite — SQLite connection string.
        PostgreSQL — PostgreSQL connection string.
        """
        if self.DATABASE_TYPE == "sqlite":
            return "sqlite+aiosqlite:///./ice_cream.db"

        return str(self.POSTGRES_DSN)

    # ADMIN
    ADMIN_INTERFACE_PORT: int = 8001
    ADMIN_SECRET_KEY: SecretStr = SecretStr("secretkey")
    ADMIN_LOGIN: SecretStr = SecretStr("admin")
    ADMIN_PASSWORD: SecretStr = SecretStr("admin")
