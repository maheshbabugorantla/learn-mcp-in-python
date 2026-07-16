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


# --- saying no, usefully --------------------------------------------------


def handle_unauthorized(request: Request) -> Response:
    """401. You didn't send a token.

    The `WWW-Authenticate` header is what makes a 401 different from a slammed
    door: it names the scheme the client should use. `realm` is a label for the
    protected area — clients show it to people, and it's a hint that this is
    EpicMe asking, not some other server in the chain.
    """
    return Response(
        "Unauthorized",
        status_code=401,
        headers={"WWW-Authenticate": 'Bearer realm="EpicMe"'},
    )
