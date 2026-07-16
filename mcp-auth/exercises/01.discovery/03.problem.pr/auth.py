"""Everything your resource server knows about who's calling.

Right now it can:

  - say where the authorization server is       (01.discovery)
"""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse

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


# TODO: Describe this resource server.
#
# Write `def handle_oauth_protected_resource_request(request: Request)`. It
# returns JSON with two keys:
#
#   resource:               the URL of this MCP server's endpoint — "/mcp" on
#                           this same host. Build it from the incoming request:
#                           str(request.url.replace(path="/mcp", query=""))
#   authorization_servers:  a list with AUTH_SERVER_URL in it
#
# This is the document the `resource_metadata` in your 401 will point at, and
# it's the hinge of the whole flow: it's how a client that has only ever heard
# of *your* server finds out who issues tokens for it.
