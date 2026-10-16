import dataclasses
from typing import TYPE_CHECKING

from asgi_lifespan import LifespanManager
from fastapi import status
from httpx import ASGITransport, AsyncClient
from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind

from app.application import build_app
from app.settings import Settings, settings


if TYPE_CHECKING:
    import pytest


async def _trace_list_decks(monkeypatch: pytest.MonkeyPatch) -> tuple[ReadableSpan, ...]:
    traced_config = dataclasses.replace(settings.api_bootstrapper_config, opentelemetry_log_traces=True)
    monkeypatch.setattr(Settings, "api_bootstrapper_config", traced_config)
    exporter = InMemorySpanExporter()
    app = build_app()
    tracer_provider = trace.get_tracer_provider()
    assert isinstance(tracer_provider, TracerProvider)
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

    async with LifespanManager(app), AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/decks/")

    assert response.status_code == status.HTTP_200_OK
    return exporter.get_finished_spans()


async def test_db_queries_produce_sqlalchemy_spans(monkeypatch: pytest.MonkeyPatch) -> None:
    db_spans = [
        span
        for span in await _trace_list_decks(monkeypatch)
        if span.instrumentation_scope is not None
        and span.instrumentation_scope.name == "opentelemetry.instrumentation.sqlalchemy"
        and span.name.startswith("SELECT")
    ]
    assert db_spans
    assert all(span.parent is not None for span in db_spans)


async def test_request_has_no_asgi_event_spans(monkeypatch: pytest.MonkeyPatch) -> None:
    request_spans = [
        span
        for span in await _trace_list_decks(monkeypatch)
        if span.instrumentation_scope is None
        or span.instrumentation_scope.name != "opentelemetry.instrumentation.sqlalchemy"
    ]
    assert [span.kind for span in request_spans] == [SpanKind.SERVER]
