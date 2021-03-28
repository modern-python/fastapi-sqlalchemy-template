from logging.handlers import SYSLOG_UDP_PORT

from pydantic import BaseSettings
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):  # pylint: disable=too-few-public-methods
    SERVICE_NAME = "FastApi"
    DEBUG = False

    LOG_LEVEL = "INFO"
    SYSLOG_HOST = "127.0.0.1"
    SYSLOG_PORT = SYSLOG_UDP_PORT

    DB_DRIVER = "postgresql+asyncpg"
    DB_HOST = "db"
    DB_PORT = 5432
    DB_USER = "postgres"
    DB_PASSWORD = "password"
    DB_DATABASE = "postgres"

    DB_POOL_SIZE = 5
    DB_MAX_OVERFLOW = 0
    DB_ECHO = False

    @property
    def DB_DSN(self) -> URL:  # pylint: disable=invalid-name
        return URL.create(
            self.DB_DRIVER,
            self.DB_USER,
            self.DB_PASSWORD,
            self.DB_HOST,
            self.DB_PORT,
            self.DB_DATABASE,
        )

    class Config:  # pylint: disable=too-few-public-methods
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
