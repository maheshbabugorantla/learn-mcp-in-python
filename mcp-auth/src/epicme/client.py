"""How your resource server reaches the authorization server.

Infrastructure, not the lesson — you never edit this, but you will *call* it,
so it's worth thirty seconds.

`AUTH_SERVER_URL` is where the EpicMe authorization server lives. `get_http()`
hands you an `httpx.AsyncClient` pointed at it:

    from epicme.client import get_http

    response = await get_http().post("/oauth/introspection", data={"token": token})

Why go through a function instead of importing a client object? Because the
tests swap what's behind it. When you run `uv run epicme-auth`, this talks to
localhost over a real socket. Under pytest it's rewired to call the auth server
in the same process, with no socket at all — same code, no ports to collide, no
background process to wait for. Upstream gets this by running the EpicMe app as
a sidecar; a function you can swap is the cheaper Python version of the same
idea.
"""

from __future__ import annotations

import httpx

from epicme.auth_server import AUTH_SERVER_URL

__all__ = ["AUTH_SERVER_URL", "get_http", "set_http", "reset_http"]

_client: httpx.AsyncClient | None = None


def get_http() -> httpx.AsyncClient:
    """An HTTP client whose base URL is the authorization server."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(base_url=AUTH_SERVER_URL, timeout=10)
    return _client


def set_http(client: httpx.AsyncClient) -> None:
    """Point `get_http()` somewhere else. Tests use this; your code shouldn't."""
    global _client
    _client = client


def reset_http() -> None:
    global _client
    _client = None
