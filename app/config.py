from pydantic import BaseSettings
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
    SERVICE_NAME: str = "FastApi"
    DEBUG: bool = False

    DB_DRIVER: str = "postgresql+asyncpg"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_DATABASE: str = "postgres"

    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 0
    DB_ECHO: bool = False

    @property
    def DB_DSN(self) -> URL:
        return URL.create(
            self.DB_DRIVER,
            self.DB_USER,
            self.DB_PASSWORD,
            self.DB_HOST,
            self.DB_PORT,
            self.DB_DATABASE,
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
