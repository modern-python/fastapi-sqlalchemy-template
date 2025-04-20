import pydantic_settings
from sqlalchemy.engine.url import URL


class Settings(pydantic_settings.BaseSettings):
    service_name: str = "FastAPI template"
    service_version: str = "1.0.0"
    service_environment: str = "local"
    service_debug: bool = False
    log_level: str = "info"

    db_driver: str = "postgresql+asyncpg"
    db_host: str = "db"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "password"
    db_database: str = "postgres"

    db_pool_size: int = 5
    db_max_overflow: int = 0
    db_echo: bool = False
    db_pool_pre_ping: bool = True

    app_port: int = 8000

    opentelemetry_endpoint: str = ""
    sentry_dsn: str = ""
    logging_buffer_capacity: int = 0
    swagger_offline_docs: bool = True

    cors_allowed_origins: list[str] = ["http://localhost:5173"]
    cors_allowed_methods: list[str] = [""]
    cors_allowed_headers: list[str] = [""]
    cors_exposed_headers: list[str] = []

    @property
    def db_dsn(self) -> URL:
        return URL.create(
            self.db_driver,
            self.db_user,
            self.db_password,
            self.db_host,
            self.db_port,
            self.db_database,
        )


settings = Settings()
