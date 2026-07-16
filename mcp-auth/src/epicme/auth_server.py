"""The EpicMe authorization server, as an ASGI app.

Infrastructure, not the lesson — you never edit this. In the TypeScript workshop
this is a whole separate app running beside your MCP server; here it's a
Starlette app you can run with `uv run epicme-auth` or mount in-process from a
test.

**This is the other end of everything you build.** Your MCP server is the
*resource server*: it holds the journal. This is the *authorization server*: it
holds the users and issues the tokens. Keeping them apart is the entire reason
the discovery and introspection dance in this course exists — if one process did
both, it could just look in a variable.

Most of the routes below come free from the SDK's `create_auth_routes`, which
builds a spec-compliant `/authorize`, `/token`, `/register`, `/revoke` and the
`/.well-known/oauth-authorization-server` metadata document. Three are ours:

    /oauth/consent          the "who are you, and do you approve?" screen
    /oauth/introspection    "what does this token mean?" — RFC 7662
    /oauth/userinfo         "who does this token belong to?"

`/oauth/introspection` is hand-written because the SDK doesn't ship an
introspection endpoint — and because it's the endpoint your resource server
spends the whole of `03.auth-info` learning to call.
"""

from __future__ import annotations

import html

from mcp.server.auth.routes import build_metadata, create_auth_routes
from mcp.server.auth.settings import ClientRegistrationOptions, RevocationOptions
from pydantic import AnyHttpUrl
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from starlette.routing import Route

from epicme.provider import SUPPORTED_SCOPES, USERS, EpicMeProvider

AUTH_SERVER_PORT = 7788
AUTH_SERVER_URL = f"http://localhost:{AUTH_SERVER_PORT}"

#: One provider instance for the process. Tests reach in and `mint_token()`.
provider = EpicMeProvider()


# --- the consent screen ---------------------------------------------------

_CONSENT_PAGE = """
<!doctype html>
<title>EpicMe — Authorize</title>
<style>
  body {{ font: 16px/1.5 system-ui, sans-serif; max-width: 34rem; margin: 4rem auto;
         padding: 0 1rem; color: #222; }}
  .scopes {{ background: #f5f5f5; border-radius: 8px; padding: 1rem 1.25rem; }}
  code {{ background: #fff; padding: .1rem .35rem; border-radius: 4px; }}
  button {{ font: inherit; padding: .6rem 1rem; border-radius: 6px; border: 0;
            background: #2563eb; color: #fff; cursor: pointer; }}
  select {{ font: inherit; padding: .4rem; }}
</style>
<h1>Authorize {client}</h1>
<p><strong>{client}</strong> wants to access your EpicMe journal.</p>
<div class="scopes">
  <p>It's asking to:</p>
  <ul>{scopes}</ul>
</div>
<form method="post">
  <p>
    <label>Sign in as
      <select name="user_id">{users}</select>
    </label>
  </p>
  <button type="submit">Approve</button>
</form>
"""

_SCOPE_HELP = {
    "user:read": "see who you are",
    "entries:read": "read your journal entries",
    "entries:write": "write journal entries",
    "tags:read": "read your tags",
    "tags:write": "create tags",
}


async def consent(request: Request) -> Response:
    consent_id = request.query_params.get("consent_id", "")
    if consent_id not in provider.pending:
        return HTMLResponse("<h1>This authorization request expired.</h1>", 400)

    if request.method == "POST":
        form = await request.form()
        user_id = str(form.get("user_id") or "")
        if user_id not in USERS:
            return HTMLResponse("<h1>Unknown user.</h1>", 400)
        return RedirectResponse(provider.complete_consent(consent_id, user_id), 302)

    client, params = provider.pending[consent_id]
    scopes = params.scopes or []
    return HTMLResponse(
        _CONSENT_PAGE.format(
            client=html.escape(client.client_name or client.client_id),
            scopes="".join(
                f"<li>{_SCOPE_HELP.get(s, s)} (<code>{html.escape(s)}</code>)</li>"
                for s in scopes
            )
            or "<li>nothing in particular</li>",
            users="".join(
                f'<option value="{u.id}">{html.escape(u.username)}</option>'
                for u in USERS.values()
            ),
        )
    )


# --- introspection (RFC 7662) --------------------------------------------


async def introspection(request: Request) -> Response:
    """Tell a resource server what an opaque token means.

    The shape of this response is what your `resolve_auth_info` parses in
    `03.auth-info`. Note the two very different bodies: a live token gets its
    claims, and anything else gets `{"active": false}` and nothing more. That
    asymmetry is the spec being careful — an unknown token, an expired one, and
    a revoked one all look identical, so nobody can probe this endpoint to learn
    which tokens once existed.
    """
    form = await request.form()
    token = str(form.get("token") or "")
    access = await provider.load_access_token(token)
    if access is None:
        return JSONResponse({"active": False})

    return JSONResponse(
        {
            "active": True,
            "client_id": access.client_id,
            "scope": " ".join(access.scopes),
            "sub": access.subject,
            "exp": access.expires_at,
            "token_type": "Bearer",
        }
    )


async def userinfo(request: Request) -> Response:
    """The user's profile, for whoever holds a token with `user:read`."""
    header = request.headers.get("authorization", "")
    token = header.removeprefix("Bearer ").removeprefix("bearer ")
    access = await provider.load_access_token(token)
    if access is None:
        return JSONResponse(
            {"error": "invalid_token"},
            status_code=401,
            headers={"WWW-Authenticate": 'Bearer realm="EpicMe", error="invalid_token"'},
        )
    if "user:read" not in access.scopes:
        return JSONResponse(
            {"error": "insufficient_scope"},
            status_code=403,
            headers={
                "WWW-Authenticate": 'Bearer realm="EpicMe", error="insufficient_scope",'
                ' scope="user:read"'
            },
        )
    user = USERS.get(access.subject or "")
    if user is None:
        return JSONResponse({"error": "not_found"}, status_code=404)
    return JSONResponse({"sub": user.id, "username": user.username, "email": user.email})


async def healthcheck(request: Request) -> Response:
    return Response("OK")


def create_auth_server_app() -> Starlette:
    issuer = AnyHttpUrl(AUTH_SERVER_URL)
    registration = ClientRegistrationOptions(
        enabled=True,
        valid_scopes=SUPPORTED_SCOPES,
        default_scopes=SUPPORTED_SCOPES,
    )
    revocation = RevocationOptions(enabled=True)

    # The SDK's metadata document doesn't know about the introspection endpoint
    # we added, so advertise it ourselves. A client (or your resource server)
    # that reads this metadata can then find introspection without hardcoding
    # the path — which is the entire promise of discovery.
    metadata = build_metadata(issuer, None, registration, revocation)
    metadata_dict = metadata.model_dump(exclude_none=True, mode="json")
    metadata_dict["introspection_endpoint"] = f"{AUTH_SERVER_URL}/oauth/introspection"
    metadata_dict["userinfo_endpoint"] = f"{AUTH_SERVER_URL}/oauth/userinfo"

    async def metadata_route(request: Request) -> Response:
        return JSONResponse(metadata_dict)

    sdk_routes = [
        route
        for route in create_auth_routes(
            provider=provider,
            issuer_url=issuer,
            client_registration_options=registration,
            revocation_options=revocation,
        )
        if getattr(route, "path", None) != "/.well-known/oauth-authorization-server"
    ]

    return Starlette(
        routes=[
            Route(
                "/.well-known/oauth-authorization-server",
                metadata_route,
                methods=["GET", "OPTIONS"],
            ),
            *sdk_routes,
            Route("/oauth/consent", consent, methods=["GET", "POST"]),
            Route("/oauth/introspection", introspection, methods=["POST"]),
            Route("/oauth/userinfo", userinfo, methods=["GET"]),
            Route("/healthcheck", healthcheck),
        ],
        # An authorization server gets talked to by browsers from other origins,
        # so it says yes to all of them. Your *resource* server is pickier —
        # deciding exactly how picky is `01.discovery`.
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["*"],
                expose_headers=["WWW-Authenticate"],
            )
        ],
    )


auth_app = create_auth_server_app()
