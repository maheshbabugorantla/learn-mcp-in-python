"""Everything your resource server knows about who's calling.

Right now it can:

  - say where the authorization server is       (01.discovery)
  - describe itself to clients                  (01.discovery)
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


# --- saying no, usefully --------------------------------------------------


# TODO: Say no, in a way the client can act on.
#
# Write `def handle_unauthorized(request: Request) -> Response` returning a 401
# with a `WWW-Authenticate` header:
#
#   Response("Unauthorized", status_code=401,
#            headers={"WWW-Authenticate": 'Bearer realm="EpicMe"'})
#
# `Bearer` names the scheme the client should use. `realm` labels the protected
# area — it's what a client can show a person so they know *what* is asking them
# to log in.
