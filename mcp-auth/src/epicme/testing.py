"""Test plumbing shared by every exercise.

Infrastructure, not the lesson. Each exercise's `conftest.py` is three lines
that pull fixtures from here, so the interesting part of a test file is the
assertions.

What it does: wires `epicme.client.get_http()` to call the authorization server
in-process, and gives you tokens to test with.

    def test_something(client, token):
        response = mcp_request(client, "tools/list", token=token)

Fixtures:
    auth_server   the authorization server app, rewired in-process (autouse)
    token         an access token for kody, with every scope
    other_token   an access token for olivia — for proving journals don't leak
    make_token    mint a token with specific scopes: make_token("entries:read")
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from starlette.testclient import TestClient

from epicme import client as client_module
from epicme.auth_server import AUTH_SERVER_URL, auth_app, provider
from epicme.provider import SUPPORTED_SCOPES

KODY = "user-kody"
OLIVIA = "user-olivia"

MCP_HEADERS = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json",
}

INITIALIZE_PARAMS = {
    "protocolVersion": "2025-06-18",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1.0"},
}


@pytest.fixture(autouse=True)
def auth_server():
    """Make `get_http()` talk to the auth server in this process, not a socket."""
    transport = httpx.ASGITransport(app=auth_app)
    http = httpx.AsyncClient(transport=transport, base_url=AUTH_SERVER_URL)
    client_module.set_http(http)
    yield auth_app
    client_module.reset_http()


@pytest.fixture
def make_token():
    def _make(*scopes: str, user_id: str = KODY) -> str:
        return provider.mint_token(
            user_id=user_id, scopes=list(scopes) if scopes else list(SUPPORTED_SCOPES)
        )

    return _make


@pytest.fixture
def token(make_token) -> str:
    return make_token()


@pytest.fixture
def other_token(make_token) -> str:
    return make_token(user_id=OLIVIA)


def mcp_request(
    client: TestClient,
    method: str,
    params: dict[str, Any] | None = None,
    token: str | None = None,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    """Send one JSON-RPC request to /mcp. Returns the raw HTTP response."""
    request_headers = dict(MCP_HEADERS)
    if token:
        request_headers["Authorization"] = f"Bearer {token}"
    if headers:
        request_headers.update(headers)
    return client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}},
        headers=request_headers,
    )


def mcp_result(response: httpx.Response) -> dict[str, Any]:
    """Pull the JSON-RPC `result` out, failing loudly if it isn't there."""
    assert response.status_code == 200, (
        f"expected a 200 from /mcp, got {response.status_code}: {response.text[:400]}"
    )
    body = response.json()
    assert "result" in body, f"expected a result, got: {body}"
    return body["result"]


def call_tool(
    client: TestClient, name: str, arguments: dict[str, Any] | None = None, *, token: str
) -> dict[str, Any]:
    """initialize, then call one tool, and hand back the tool result."""
    mcp_request(client, "initialize", INITIALIZE_PARAMS, token=token)
    response = mcp_request(
        client, "tools/call", {"name": name, "arguments": arguments or {}}, token=token
    )
    return mcp_result(response)


def tool_text(result: dict[str, Any]) -> str:
    """All the text content of a tool result, joined."""
    return "\n".join(
        block.get("text", "")
        for block in result.get("content", [])
        if block.get("type") == "text"
    )
