"""The front door.

Everything arrives here first. This file decides what's public, what needs a
token, and what a rejected request gets told.
"""
from __future__ import annotations

from collections.abc import Mapping

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route

from auth import handle_oauth_authorization_server_request, handle_oauth_protected_resource_request
from server import mcp
from utils import WithCors


def get_cors_headers(request: Request) -> Mapping[str, str] | None:
    """Which requests get CORS headers, and which headers they get."""
    if "/.well-known" not in str(request.url):
        # /mcp is not browser-facing, so it gets nothing. Handing out CORS
        # headers you don't need is how origins you never thought about end up
        # able to call your server.
        return None
    return {
        # We can't know every origin that might want to read our metadata, and
        # there's nothing secret in it — it's a public description of how to
        # log in. So: anyone.
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
        # Clients are supposed to send this on every request. Not all do, but
        # allowing it costs nothing.
        "Access-Control-Allow-Headers": "mcp-protocol-version",
    }

# TODO: Guard /mcp.
#
# Write `async def authorize(request: Request) -> Response | None`. Return a
# Response to reject the request, or None to let it through.
#
# For now, just check that the request carries an Authorization header at all:
#
#   if "authorization" not in request.headers:
#       return handle_unauthorized(request)
#   return None
#
# That's not real authentication — anyone who types the word "Bearer" gets in —
# and you'll fix it in `03.auth-info`. Checking for the header is the first step
# of every OAuth flow, and it's what makes the client go looking for a token.
#
# Then wire it up: wrap the mounted MCP app in `WithAuth(..., authorize)` down
# in `routes` below.

async def healthcheck(request: Request) -> Response:
    return Response("OK")


app = Starlette(
    routes=[
        Route("/healthcheck", healthcheck),
        Route(
            "/.well-known/oauth-authorization-server",
            handle_oauth_authorization_server_request,
        ),
        Route(
            "/.well-known/oauth-protected-resource/mcp",
            handle_oauth_protected_resource_request,
        ),
        # The MCP endpoint. Wide open for now — nothing is checking who this is.
        Mount("/mcp", app=mcp.streamable_http_app()),
    ],
    # The MCP session manager has to be running for /mcp to work at all.
    lifespan=lambda app: mcp.session_manager.run(),
)

# CORS wraps everything, so even a 404 comes back readable in a browser.
app = WithCors(app, get_cors_headers)
