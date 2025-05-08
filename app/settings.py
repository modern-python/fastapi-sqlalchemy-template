import pydantic_settings
from lite_bootstrap import FastAPIConfig
from sqlalchemy.engine.url import URL, make_url


class Settings(pydantic_settings.BaseSettings):
    service_name: str = "FastAPI template"
    service_version: str = "1.0.0"
    service_environment: str = "local"
    service_debug: bool = False
    log_level: str = "info"

    db_dsn: str = "postgresql+asyncpg://postgres:password@db/postgres"
    db_pool_size: int = 5
    db_max_overflow: int = 0
    db_pool_pre_ping: bool = True

    app_host: str = "0.0.0.0"  # noqa: S104
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
    def db_dsn_parsed(self) -> URL:
        return make_url(self.db_dsn)

    @property
    def api_bootstrapper_config(self) -> FastAPIConfig:
        return FastAPIConfig(
            service_name=settings.service_name,
            service_version=settings.service_version,
            service_environment=settings.service_environment,
            service_debug=settings.service_debug,
            opentelemetry_endpoint=settings.opentelemetry_endpoint,
            sentry_dsn=settings.sentry_dsn,
            cors_allowed_origins=settings.cors_allowed_origins,
            cors_allowed_methods=settings.cors_allowed_methods,
            cors_allowed_headers=settings.cors_allowed_headers,
            cors_exposed_headers=settings.cors_exposed_headers,
            logging_buffer_capacity=settings.logging_buffer_capacity,
            swagger_offline_docs=settings.swagger_offline_docs,
        )


settings = Settings()
