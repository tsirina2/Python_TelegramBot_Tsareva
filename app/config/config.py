import os

from pydantic import PostgresDsn,SecretStr,Secret
from pydantic_settings import BaseSettings,SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file= os.path.join(os.path.dirname(__file__), ".envs/.env"))

    TELEGRAM_API_KEY: SecretStr
    LOG_LEVEL:str = "INFO"


    POSTGRES_USER: str ="postgres"
    POSTGRES_PASSWORD: SecretStr = SecretStr("postgres")
    POSTGRES_HOST:str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgres"


    @property
    def POSTGRES_DSN(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme= "postgresql",
            username = self.POSTGRES_USER,
            password = self.POSTGRES_PASSWORD.get_secret_value(),
            host = self.POSTGRES_HOST,
            port= self.POSTGRES_PORT,
            path = f"/{self.POSTGRES_DB}"
        )





