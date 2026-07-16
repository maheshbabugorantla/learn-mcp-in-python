"""Everything your resource server knows about who's calling.

Right now it can:

  - say where the authorization server is       (01.discovery)
  - describe itself to clients                  (01.discovery)
  - turn away requests with no usable token     (02.init)
"""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from epicme.client import AUTH_SERVER_URL, get_http


# --- discovery: how a client finds its way in -----------------------------


async def handle_oauth_authorization_server_request(request: Request) -> Response:
    """Pass the authorization server's metadata along to whoever asks.

    Strictly, a client that read our protected resource metadata could go fetch
    this from the authorization server itself. We serve a copy because some
    clients look for it here first, and forwarding it is three lines.
    """
    response = await get_http().get("/.well-known/oauth-authorization-server")
    return JSONResponse(response.json())


def handle_oauth_protected_resource_request(request: Request) -> Response:
    """Describe this resource server: what it is, who vouches for it."""
    return JSONResponse(
        {
            "resource": str(request.url.replace(path="/mcp", query="")),
            "authorization_servers": [AUTH_SERVER_URL],
        }
    )


def resource_metadata_url(request: Request) -> str:
    """Where this server's protected resource metadata lives."""
    return str(
        request.url.replace(path="/.well-known/oauth-protected-resource/mcp", query="")
    )


# --- saying no, usefully --------------------------------------------------


def handle_unauthorized(request: Request) -> Response:
    """401. You didn't send a usable token.

    `resource_metadata` is what turns a 401 from a dead end into instructions.
    It points at the document that names our authorization server, so a client
    that has never seen this server before can read it, register itself, send
    the user to log in, and come back with a token — without a human ever
    configuring anything.
    """
    auth_params = [
        'Bearer realm="EpicMe"',
        f'resource_metadata="{resource_metadata_url(request)}"',
    ]
    return Response(
        "Unauthorized",
        status_code=401,
        headers={"WWW-Authenticate": ", ".join(auth_params)},
    )
