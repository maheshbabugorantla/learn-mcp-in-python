"""Everything your resource server knows about who's calling.

Right now it can:

  - say where the authorization server is       (01.discovery)
  - describe itself to clients                  (01.discovery)
  - turn away requests with no usable token     (02.init)
  - turn an opaque token into a user            (03.auth-info)
  - carry that user to your tools               (04.user)
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from epicme.client import AUTH_SERVER_URL, get_http


# --- who's calling --------------------------------------------------------


class AuthInfo(BaseModel):
    """The useful facts about the caller, dug out of their access token."""

    token: str
    client_id: str
    scopes: list[str]
    user_id: str


class User(BaseModel):
    """A person, according to the authorization server."""

    sub: str
    username: str
    email: str


class ActiveToken(BaseModel):
    active: Literal[True]
    client_id: str
    scope: str
    sub: str


class InactiveToken(BaseModel):
    # Deliberately nothing else. A dead token tells you it's dead and no more.
    active: Literal[False]


#: An introspection response is one of two quite different shapes, told apart by
#: `active`. Modelling it as a discriminated union means you cannot read `sub`
#: off a dead token by accident — there is no `sub` on that branch to read.
IntrospectionResponse = Annotated[
    ActiveToken | InactiveToken, Field(discriminator="active")
]
_introspection_response = TypeAdapter(IntrospectionResponse)


async def resolve_auth_info(auth_header: str | None) -> AuthInfo | None:
    """Turn an `Authorization` header into an `AuthInfo`, or `None`.

    `None` means "no usable token" and covers every way that can happen: no
    header, a header we can't parse, a token the authorization server has never
    heard of, an expired one, a revoked one. The caller doesn't get to know
    which, and neither do we.
    """
    if not auth_header:
        return None

    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    token = token.strip()

    response = await get_http().post("/oauth/introspection", data={"token": token})
    if response.status_code != 200:
        return None

    data = _introspection_response.validate_python(response.json())
    if not data.active:
        return None

    return AuthInfo(
        token=token,
        client_id=data.client_id,
        # The wire format is one space-separated string; a list is nicer to work
        # with, and this is the last place that has to care about the difference.
        scopes=data.scope.split(),
        user_id=data.sub,
    )


async def fetch_user(auth_info: AuthInfo) -> User | None:
    """Ask the authorization server who this token belongs to."""
    response = await get_http().get(
        "/oauth/userinfo", headers={"Authorization": f"Bearer {auth_info.token}"}
    )
    if response.status_code != 200:
        return None
    return User.model_validate(response.json())


# --- carrying the caller into your tools ----------------------------------

#: Set once per request by `app.py`, read by your tools.
#:
#: A tool is a plain function — nobody hands it the request. A ContextVar is how
#: Python passes something to code it isn't calling directly: set it at the
#: front door and any code running for that request can read it. This is what
#: `ctx.props` does in the Cloudflare version of this workshop, minus the
#: Cloudflare.
current_auth_info: ContextVar[AuthInfo | None] = ContextVar(
    "current_auth_info", default=None
)


def require_auth_info() -> AuthInfo:
    """The caller, or an exception if there isn't one.

    By the time a tool runs, `app.py` has already turned away everyone without a
    token, so this never fires in practice. It's here so that if someone later
    mounts the MCP app without the auth middleware, the server fails loudly
    instead of quietly serving a journal to nobody in particular.
    """
    auth_info = current_auth_info.get()
    if auth_info is None:
        raise RuntimeError(
            "No auth info on this request — is the MCP app still wrapped in WithAuth?"
        )
    return auth_info


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
    """401. Either you sent no token, or the one you sent is no good.

    The `WWW-Authenticate` header is the interesting part: it's how a 401 stops
    being a dead end. `resource_metadata` points at the document that names our
    authorization server, so a client that has never seen this server before can
    read it, register itself, send the user to log in, and come back with a
    token — without a human ever configuring anything.
    """
    had_a_token = "authorization" in request.headers
    auth_params = [
        'Bearer realm="EpicMe"',
        # Only say the token is invalid if they actually sent one. Telling a
        # client its (nonexistent) token is invalid sends it off to refresh
        # something it doesn't have.
        *(
            [
                'error="invalid_token"',
                'error_description="The access token is invalid or expired"',
            ]
            if had_a_token
            else []
        ),
        f'resource_metadata="{resource_metadata_url(request)}"',
    ]
    return Response(
        "Unauthorized",
        status_code=401,
        headers={"WWW-Authenticate": ", ".join(auth_params)},
    )
