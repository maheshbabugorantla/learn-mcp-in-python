"""The front door.

Everything arrives here first. This file decides what's public, what needs a
token, and what a rejected request gets told.

Four things live at the edge:

    /healthcheck                                    open to anyone
    /.well-known/oauth-authorization-server         open — it's how clients find the AS
    /.well-known/oauth-protected-resource/mcp       open — it's how clients find *us*
    /mcp                                            token required

The two metadata documents have to be readable *without* a token. That looks
wrong the first time you see it on an auth checklist, but a client with no token
is exactly who needs them: they're the instructions for getting one.
"""
from __future__ import annotations

from collections.abc import Mapping

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route

from auth import (
    current_auth_info,
    handle_insufficient_scope,
    handle_oauth_authorization_server_request,
    handle_oauth_protected_resource_request,
    handle_unauthorized,
    has_sufficient_scope,
    resolve_auth_info,
)
from server import mcp
from utils import WithAuth, WithCors


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

async def authorize(request: Request) -> Response | None:
    """Guard `/mcp`. Return a response to reject, or `None` to allow.

    In order, and the order is the point:

      1. Is there a usable token?     no  -> 401, go get one
      2. Can it do anything here?     no  -> 403, that token will never work
      3. Who is it?                   -> stash it where the tools can find it

    Per-tool permissions are *not* decided here. This only asks whether the
    request is worth handling at all; `require_scope` in `server.py` decides
    whether this particular tool is allowed.
    """
    auth_info = await resolve_auth_info(request.headers.get("authorization"))
    if auth_info is None:
        return handle_unauthorized(request)

    if not has_sufficient_scope(auth_info):
        return handle_insufficient_scope()

    current_auth_info.set(auth_info)

    return None

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
        # Mounted at `/mcp` exactly, so the guard covers the MCP endpoint and
        # nothing else. Mount it at `/` and every unmatched path — every typo a
        # client makes — starts demanding a token instead of saying 404.
        Mount("/mcp", app=WithAuth(mcp.streamable_http_app(), authorize)),
    ],
    # The MCP session manager has to be running for /mcp to work at all.
    lifespan=lambda app: mcp.session_manager.run(),
)

# CORS wraps everything, so even a 404 comes back readable in a browser.
app = WithCors(app, get_cors_headers)
