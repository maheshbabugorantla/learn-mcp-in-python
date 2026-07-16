"""The EpicMe authorization server's brain.

Infrastructure, not the lesson — you never edit this. It exists so the course
has a real OAuth 2.1 authorization server to talk to, the same way upstream's
TypeScript workshop runs a separate EpicMe app alongside your MCP server.

It's an in-memory implementation of the SDK's `OAuthAuthorizationServerProvider`
protocol: it registers clients, issues authorization codes, and swaps them for
access tokens. Everything lives in dictionaries and disappears when the process
does, which is exactly what you want for a course and exactly what you must not
ship.

The one thing worth knowing as you work: a token here is an opaque random
string, not a JWT. Nothing about the user is encoded *in* the token — the only
way to find out who it belongs to is to ask this server. That asking is called
introspection, and it's what you build in `03.auth-info`.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    OAuthAuthorizationServerProvider,
    RefreshToken,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

#: Every scope this authorization server knows how to issue.
SUPPORTED_SCOPES = [
    "user:read",
    "entries:read",
    "entries:write",
    "tags:read",
    "tags:write",
]

ACCESS_TOKEN_LIFETIME = 60 * 60  # one hour


@dataclass
class User:
    """A person with a journal."""

    id: str
    username: str
    email: str


#: The course ships with two users so you can prove one can't read the other's
#: journal. There's no password: the consent screen just asks which one you are.
USERS: dict[str, User] = {
    "user-kody": User(id="user-kody", username="kody", email="kody@epicme.test"),
    "user-olivia": User(id="user-olivia", username="olivia", email="olivia@epicme.test"),
}

DEFAULT_USER_ID = "user-kody"


class EpicMeProvider(OAuthAuthorizationServerProvider):
    """An in-memory OAuth 2.1 provider. Real enough to learn on, not to deploy."""

    def __init__(self) -> None:
        self.clients: dict[str, OAuthClientInformationFull] = {}
        self.auth_codes: dict[str, AuthorizationCode] = {}
        self.access_tokens: dict[str, AccessToken] = {}
        self.refresh_tokens: dict[str, RefreshToken] = {}
        #: pending consent requests, keyed by the id in the consent URL
        self.pending: dict[str, tuple[OAuthClientInformationFull, AuthorizationParams]] = {}

    # --- clients (dynamic client registration) ---------------------------

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self.clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        self.clients[client_info.client_id] = client_info

    # --- the authorization step ------------------------------------------

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        """Send the user to a consent screen rather than silently approving.

        A real server would make them log in here. We show a page that says who
        is asking and for what, and lets you pick a user.
        """
        consent_id = secrets.token_urlsafe(16)
        self.pending[consent_id] = (client, params)
        return f"/oauth/consent?consent_id={consent_id}"

    def complete_consent(self, consent_id: str, user_id: str) -> str:
        """Called by the consent page once someone approves. Returns a redirect."""
        client, params = self.pending.pop(consent_id)
        code = secrets.token_urlsafe(32)
        self.auth_codes[code] = AuthorizationCode(
            code=code,
            scopes=params.scopes or [],
            expires_at=time.time() + 300,
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
            subject=user_id,
        )
        return construct_redirect_uri(
            str(params.redirect_uri), code=code, state=params.state
        )

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        code = self.auth_codes.get(authorization_code)
        if code is None or code.client_id != client.client_id:
            return None
        return code

    # --- swapping a code for a token -------------------------------------

    def _issue(
        self, client_id: str, scopes: list[str], subject: str | None, resource: str | None
    ) -> OAuthToken:
        access = secrets.token_urlsafe(32)
        refresh = secrets.token_urlsafe(32)
        self.access_tokens[access] = AccessToken(
            token=access,
            client_id=client_id,
            scopes=scopes,
            expires_at=int(time.time()) + ACCESS_TOKEN_LIFETIME,
            resource=resource,
            subject=subject,
        )
        self.refresh_tokens[refresh] = RefreshToken(
            token=refresh, client_id=client_id, scopes=scopes, subject=subject
        )
        return OAuthToken(
            access_token=access,
            token_type="Bearer",
            expires_in=ACCESS_TOKEN_LIFETIME,
            scope=" ".join(scopes),
            refresh_token=refresh,
        )

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        self.auth_codes.pop(authorization_code.code, None)
        return self._issue(
            client.client_id,
            authorization_code.scopes,
            authorization_code.subject,
            authorization_code.resource,
        )

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> RefreshToken | None:
        token = self.refresh_tokens.get(refresh_token)
        if token is None or token.client_id != client.client_id:
            return None
        return token

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        self.refresh_tokens.pop(refresh_token.token, None)
        return self._issue(
            client.client_id,
            scopes or refresh_token.scopes,
            refresh_token.subject,
            None,
        )

    # --- reading and revoking tokens -------------------------------------

    async def load_access_token(self, token: str) -> AccessToken | None:
        access = self.access_tokens.get(token)
        if access is None:
            return None
        if access.expires_at and access.expires_at < time.time():
            # Expired tokens are indistinguishable from tokens that never
            # existed, as far as anyone asking is concerned.
            del self.access_tokens[token]
            return None
        return access

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        self.access_tokens.pop(token.token, None)
        self.refresh_tokens.pop(token.token, None)

    # --- a shortcut the tests use ----------------------------------------

    def mint_token(
        self,
        user_id: str = DEFAULT_USER_ID,
        scopes: list[str] | None = None,
        client_id: str = "test-client",
    ) -> str:
        """Issue an access token without the browser dance.

        Only tests use this. It's the moral equivalent of upstream's test-auth
        route: the OAuth flow is not what any individual test is checking, so
        skip to the part where you have a token.
        """
        token = secrets.token_urlsafe(32)
        self.access_tokens[token] = AccessToken(
            token=token,
            client_id=client_id,
            scopes=list(SUPPORTED_SCOPES if scopes is None else scopes),
            expires_at=int(time.time()) + ACCESS_TOKEN_LIFETIME,
            subject=user_id,
        )
        return token
