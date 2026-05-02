# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

Python 3.14 async REST API. FastAPI + SQLAlchemy 2 (async) + PostgreSQL + Alembic. Served by Granian (uvloop). Dependencies managed by `uv`. Linted with `ruff`, type-checked with `ty` (not mypy). Observability via `lite-bootstrap` (OpenTelemetry, Sentry). DI via `modern-di`. Repositories via `advanced-alchemy`.

## Common commands

The development workflow runs inside Docker via `just`. The `application` service mounts the repo and depends on a `db` Postgres service.

```bash
just              # default: install + lint + build + test
just run          # alembic upgrade head + start app on :8000
just sh           # shell inside the application container
just test [args]  # downgrade to base, upgrade, then pytest <args>; brings stack down after
just migration -m "msg"   # autogenerate alembic revision against current head
just lint         # eof-fixer + ruff format + ruff check --fix + ty check
just build        # docker compose build application
just down         # docker compose down --remove-orphans
just install      # uv lock --upgrade && uv sync --all-extras --all-groups --frozen
```

Running a single test (inside container or with DB available):

```bash
uv run pytest tests/test_decks.py::test_get_decks -x
```

CI (`.github/workflows/main.yml`) runs `ruff format --check`, `ruff check --no-fix`, `ty check`, then `alembic upgrade head` and `pytest` against a Postgres service. Match this locally before pushing.

## Architecture

### Request lifecycle

`app/__main__.py` boots Granian pointing at `app.application:build_app` (factory). `build_app()` in `app/application.py`:

1. Creates a `modern_di.Container` with the `Dependencies` group from `app/ioc.py`.
2. Builds a `FastAPIBootstrapper` from `settings.api_bootstrapper_config`, injecting SQLAlchemy + asyncpg OpenTelemetry instrumentors.
3. `modern_di_fastapi.setup_di(app, container)` wires DI scopes onto the FastAPI app.
4. Includes `app.api.decks.ROUTER` under `/api`.
5. Registers `DuplicateKeyError` → 422 handler from `app/exceptions.py`.

### DI scopes (modern-di)

`app/ioc.py` defines providers:
- `database_engine` — singleton-ish `AsyncEngine` with `create_sa_engine` / `close_sa_engine` finalizer.
- `session` — `Scope.REQUEST`, finalized by `close_session`.
- `decks_repository`, `cards_repository` — `Scope.REQUEST`, depend on `session`, configured with `auto_commit=True` (commit happens at session close, not per call).

Endpoints inject repositories with `FromDI(Repository)` from `modern_di_fastapi`. Add new providers to `Dependencies` rather than constructing services manually in routes.

### Database layer

- `app/models.py` — `BigIntAuditBase` from `advanced_alchemy` (auto `id`, `created_at`, `updated_at`). The module aliases `orm_registry.metadata` onto `orm.DeclarativeBase.metadata` so Alembic autogenerate sees both. New models go here.
- `app/repositories.py` — Subclass `SQLAlchemyAsyncRepositoryService[Model]` with a nested `BaseRepository(SQLAlchemyAsyncRepository[Model])`. Routes use the service methods (`list`, `get_one_or_none`, `create`, `update`, `create_many`, `upsert_many`).
- `app/resources/db.py` — `CustomAsyncSession.close()` does `expunge_all()` instead of closing when bound to an `AsyncConnection`. This is what enables the test rollback pattern below — do not "fix" it.
- `migrations/env.py` swaps the asyncpg driver for the sync `postgresql` driver and uses `app.models.METADATA` as `target_metadata`.

### Settings

`app/settings.py` — `pydantic_settings.BaseSettings`. Env vars are unprefixed (`DB_DSN`, `SERVICE_DEBUG`, `SERVICE_ENVIRONMENT`, `LOG_LEVEL`, `APP_HOST`, `APP_PORT`, `OPENTELEMETRY_ENDPOINT`, `SENTRY_DSN`, `CORS_ALLOWED_ORIGINS`, ...). `api_bootstrapper_config` produces a `FastAPIConfig` for `lite-bootstrap`.

### Tests

`tests/conftest.py` provides the test isolation pattern — read it before adding fixtures:

- `app` fixture builds a fresh app via `LifespanManager`.
- `db_session` opens a connection, begins a transaction, begins a nested savepoint, and **overrides `Dependencies.database_engine`** with the connection itself. The nested savepoint is rolled back at teardown so each test starts clean. This is why `CustomAsyncSession.close` must `expunge_all` rather than close — closing would commit the outer transaction.
- `set_async_session_in_base_sqlalchemy_factory` wires `db_session` into `SQLAlchemyFactory.__async_session__` so `polyfactory` factories in `tests/factories.py` (`DeckModelFactory`, `CardModelFactory`) persist via the rolled-back session. Test modules that use these factories opt in with `pytestmark = [pytest.mark.usefixtures("set_async_session_in_base_sqlalchemy_factory")]`.

`pytest.ini_options` sets `asyncio_mode = "auto"` — async tests do not need `@pytest.mark.asyncio`. Coverage runs by default (`--cov=. --cov-report term-missing`).

## Conventions

- Type-ignore syntax is `# ty: ignore[error-code]` (this project uses `ty`, not mypy). See `app/application.py:39` for an example.
- Ruff is configured with `select = ["ALL"]` and a curated ignore list in `pyproject.toml`. Don't sprinkle `# noqa`; prefer fixing or extending the project ignore list if a rule is genuinely wrong for the codebase.
- Routes return `typing.cast("schemas.X", obj)` over ORM/dict objects rather than constructing Pydantic models — the schemas use `from_attributes=True`.
- Line length is 120.
