from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_cors_preflight_allows_write_methods(client: AsyncClient) -> None:
    response = await client.options(
        "/api/decks/",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    allow_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allow_methods
    assert "PUT" in allow_methods
