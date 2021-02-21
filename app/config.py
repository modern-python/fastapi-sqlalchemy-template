from logging.handlers import SYSLOG_UDP_PORT
from typing import Optional

from pydantic import BaseSettings
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):  # pylint: disable=too-few-public-methods
    SERVICE_NAME = "FastApi"
    DEBUG = False

    LOG_LEVEL = "INFO"
    SYSLOG_HOST = "127.0.0.1"
    SYSLOG_PORT = SYSLOG_UDP_PORT

    DB_DRIVER = "postgresql"
    DB_HOST = "db"
    DB_PORT = 5432
    DB_USER = "postgres"
    DB_PASSWORD = "password"
    DB_DATABASE = "postgres"

    DB_POOL_MIN_SIZE = 1
    DB_POOL_MAX_SIZE = 5
    DB_ECHO = DEBUG
    DB_SSL: Optional[str] = None
    DB_RETRY_LIMIT = 5
    DB_RETRY_INTERVAL = 1
    DB_USE_CONNECTION_FOR_REQUEST = True

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
