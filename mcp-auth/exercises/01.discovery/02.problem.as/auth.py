"""Everything your resource server knows about who's calling.

Right now it can:

  - say where the authorization server is       (01.discovery)
"""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse

from epicme.client import get_http


# --- discovery: how a client finds its way in -----------------------------

# TODO: Serve the authorization server's metadata.
#
# Write `async def handle_oauth_authorization_server_request(request: Request)`.
# It should GET "/.well-known/oauth-authorization-server" from the authorization
# server and return the body as JSON:
#
#   response = await get_http().get("/.well-known/oauth-authorization-server")
#   return JSONResponse(response.json())
#
# `get_http()` is already pointed at the auth server, so a path is all you need.
