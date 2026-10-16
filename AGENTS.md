# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

Python 3.14 async REST API. FastAPI + SQLAlchemy 2 (async) + PostgreSQL + Alembic. Served by Granian (uvloop). Dependencies managed by `uv`. Linted with `ruff`, type-checked with `ty` (not mypy). Observability via `lite-bootstrap` (OpenTelemetry, Sentry). DI via `modern-di`. Repositories via `advanced-alchemy`.

## Common commands

The development workflow runs inside Docker via `just` (`just --list` / read the `justfile` for the full recipe list). The `application` service mounts the repo and depends on a `db` Postgres service. Bare `just` runs the default pipeline (install + lint + build + test).

Things the recipe names don't make obvious:

- `just test [args]` recreates a clean DB first (`alembic downgrade base` → `upgrade head`) and tears the stack down afterward; `[args]` are passed through to `pytest`.
- `just run` applies migrations then starts the app on :8000.
- `just lint` auto-fixes (eof-fixer + `ruff format` + `ruff check --fix` + `ty check`); CI (below) is the no-fix gate.

Running a single test (inside container or with DB available):

```bash
uv run pytest tests/test_decks.py::test_get_decks -x
```

CI (`.github/workflows/main.yml`) runs `ruff format --check`, `ruff check --no-fix`, `ty check`, then `alembic upgrade head` and `pytest` against a Postgres service. Match this locally before pushing.

## Architecture

### Request lifecycle

`app/__main__.py` boots Granian pointing at `app.application:build_app` (factory). `build_app()` in `app/application.py`:

1. Creates a `modern_di.Container` with `ioc.ALL_GROUPS` from `app/ioc.py`.
2. Builds a `FastAPIBootstrapper` from `settings.api_bootstrapper_config`, injecting the SQLAlchemy OpenTelemetry instrumentor.
3. `modern_di_fastapi.setup_di(app, container)` wires DI scopes onto the FastAPI app.
4. Includes one `ROUTER` per resource (`app.api.decks.ROUTER`, `app.api.cards.ROUTER`) under `/api` via `include_routers`. Add a new resource by creating `app/api/<name>.py` with its own `APIRouter`-based `ROUTER` and registering it there.
5. Registers `DuplicateKeyError` → 422 handler from `app/exceptions.py`.

### DI scopes (modern-di)

`app/ioc.py` splits providers into three groups, collected in `ALL_GROUPS`.

`Database`:
- `database_engine` — singleton-ish primary `AsyncEngine` (`create_primary_sa_engine`, `close_sa_engine` finalizer).
- `database_read_engine` — singleton-ish read `AsyncEngine` built from `DB_REPLICA_DSN`, or from `DB_DSN` when it is unset. It runs in `AUTOCOMMIT` (no BEGIN/ROLLBACK per request) and sets `default_transaction_read_only=on`, so Postgres rejects writes on it. Each statement sees its own snapshot, so a multi-query read (e.g. `fetch_with_cards`) can see a write that commits in between. Without a replica it is a second pool on the primary, so a process can hold up to `2 × db_pool_size` connections.
- `dynamic_engine` — `Scope.REQUEST`; `choose_sa_engine` returns the read engine for `GET`/`HEAD` requests, the primary otherwise (including when there is no request). GET handlers cannot write, and a read right after a write may see replica lag.
- `session` — `Scope.REQUEST`, bound to `dynamic_engine`, finalized by `close_session`.
- `transaction` — `Scope.REQUEST`, a `db_retry.Transaction` over `session`. Leaving its block rolls back anything uncommitted and closes the session.

`Repositories` (`Scope.REQUEST`): `decks_repository` and `cards_repository`, on `Database.session` with `auto_commit=False`. The use case commits through `transaction.commit()`.

`UseCases` (`Scope.REQUEST`): one provider per use case in `app/use_cases/`. modern-di fills each dataclass field by its type, so a use case needs no `kwargs`.

Endpoints inject a use case with `FromDI(UseCase)` from `modern_di_fastapi`, call it, and convert the result to a schema. They never touch repositories or the session. Add new providers to the matching group rather than constructing services manually in routes.

### Use cases and lost connections

`pool_pre_ping` is off by default (`DB_POOL_PRE_PING`). A pooled connection that died while idle is handled by `db_retry.postgres_retry` instead, which saves a round trip on every checkout. That only works if the retried function owns its whole transaction, so every use case has this shape:

```python
@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class ListDecksUseCase:
    transaction: Transaction
    decks_repository: DecksRepository

    @postgres_retry
    async def __call__(self) -> Sequence[models.Deck]:
        async with self.transaction:
            decks: typing.Final = await self.decks_repository.get_many()
            await self.transaction.commit()
        return decks
```

- Every query runs inside `async with self.transaction:`. A query before the block leaves the session in a failed transaction on a lost connection, and the retry then fails with `PendingRollbackError`.
- Commit before leaving the block, reads included, and before any early return. Otherwise `__aexit__` rolls back, which expires the loaded rows.
- A retry runs the whole use case again. If the connection drops during `COMMIT`, the write may already have landed. A write that creates rows needs something that makes the second run harmless:
  - `CreateDeckUseCase` takes a client-generated `idempotency_key` (`schemas.DeckCreate`, unique on `decks`). It looks the key up inside the transaction and returns the existing deck when it finds one, so a retry, or a client resending the request, gets the first deck back. Two concurrent requests with one key can still both miss the lookup; the second then fails on the unique constraint as a duplicate-key error.
  - `CreateCardsUseCase` relies on the `(deck_id, front)` unique constraint. A replay is rejected as a duplicate-key error rather than creating the cards twice.
  - Updates (`UpdateDeckUseCase`, `UpdateCardsUseCase`) write the same values again, so a replay is harmless.

`app/use_cases/` is exempt from ruff's `TC` rules because modern-di reads the dataclass field annotations at runtime.

### Database layer

- `app/models.py` — `BigIntAuditBase` from `advanced_alchemy` (auto `id`, `created_at`, `updated_at`). The module aliases `orm_registry.metadata` onto `orm.DeclarativeBase.metadata` so Alembic autogenerate sees both. New models go here.
- `app/repositories.py` — Subclass `SQLAlchemyAsyncRepositoryService[Model]` with a nested `BaseRepository(SQLAlchemyAsyncRepository[Model])`. Use cases call the service methods (`get_many`, `get_one`, `create`, `update`, `create_many`, `upsert_many`).
- `app/resources/db.py` — engine factories live here and are DI creators: modern-di resolves their parameter annotations at runtime, so `pyproject.toml` exempts `app/resources/` from ruff's `TC` rules. `create_session` passes `join_transaction_mode="create_savepoint"`. This is inert in production (the session binds to an engine) but enables the test rollback pattern below: when a test binds the session to a connection already in a transaction, the session owns its own savepoint so the outer transaction survives commits — do not "fix" it.
- `migrations/env.py` swaps the asyncpg driver for the sync `postgresql` driver and uses `app.models.METADATA` as `target_metadata`.

### Settings

`app/settings.py` — `pydantic_settings.BaseSettings`. Env vars are unprefixed (`DB_DSN`, `DB_REPLICA_DSN`, `SERVICE_DEBUG`, `SERVICE_ENVIRONMENT`, `LOG_LEVEL`, `APP_HOST`, `APP_PORT`, `OPENTELEMETRY_ENDPOINT`, `SENTRY_DSN`, `CORS_ALLOWED_ORIGINS`, ...). `api_bootstrapper_config` produces a `FastAPIConfig` for `lite-bootstrap`.

### Tests

`tests/conftest.py` provides the test isolation pattern — read it before adding fixtures:

- `app` fixture builds a fresh app via `LifespanManager`.
- `db_session` opens a connection, begins a transaction, and **overrides `Database.dynamic_engine`** with the connection itself, so reads and writes share one rolled-back transaction. Each session built against that connection uses `join_transaction_mode="create_savepoint"`, so `transaction.commit()` releases the session's own savepoint while the outer transaction is rolled back at teardown — each test starts clean.
- `set_async_session_in_base_sqlalchemy_factory` wires `db_session` into `SQLAlchemyFactory.__async_session__` so `polyfactory` factories in `tests/factories.py` (`DeckModelFactory`, `CardModelFactory`) persist via the rolled-back session. Test modules that use these factories opt in with `pytestmark = [pytest.mark.usefixtures("set_async_session_in_base_sqlalchemy_factory")]`.

`pytest.ini_options` sets `asyncio_mode = "auto"` — async tests do not need `@pytest.mark.asyncio`. Coverage runs by default with `--cov-fail-under=100`, so `just test` fails unless tests cover every line of new code.

## Conventions

- Ruff is configured with `select = ["ALL"]` and a curated ignore list in `pyproject.toml`. Don't sprinkle `# noqa`; prefer fixing or extending the project ignore list if a rule is genuinely wrong for the codebase.
- Routes convert ORM objects to schemas explicitly, never via `typing.cast`. Single objects: `schemas.X.model_validate(instance)`. Collections: `schemas.Xs.from_models(objects)` (the `Collection[T]` seam in `app/schemas.py`). Both rely on `from_attributes=True`.
- Deck responses are deliberately two-shaped: `list_decks`/`create_deck`/`update_deck` return the light `schemas.Deck` (no `cards`), while `get_deck` returns `schemas.DeckWithCards`. The split mirrors loading — lists/writes use `noload` (no cards query), detail uses `selectinload` via `fetch_with_cards` — so the type states exactly what each endpoint loads.
- Line length is 120.

## Agent skills

### Issue tracker

GitHub issues on `modern-python/fastapi-sqlalchemy-template`, via `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles, each label string equal to its name. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
