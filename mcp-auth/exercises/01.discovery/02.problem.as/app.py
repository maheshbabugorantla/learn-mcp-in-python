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


# TODO: Serve the metadata you just wrote a handler for.
#
# Add a route to `routes` below:
#
#   Route(
#       "/.well-known/oauth-authorization-server",
#       handle_oauth_authorization_server_request,
#   ),
#
# and import it from `auth` at the top.


async def healthcheck(request: Request) -> Response:
    return Response("OK")


app = Starlette(
    routes=[
        Route("/healthcheck", healthcheck),
        # The MCP endpoint. Wide open for now — nothing is checking who this is.
        Mount("/mcp", app=mcp.streamable_http_app()),
    ],
    # The MCP session manager has to be running for /mcp to work at all.
    lifespan=lambda app: mcp.session_manager.run(),
)

# CORS wraps everything, so even a 404 comes back readable in a browser.
app = WithCors(app, get_cors_headers)
