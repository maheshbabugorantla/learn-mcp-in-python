"""Tokens get introspected, not trusted."""

from epicme.testing import INITIALIZE_PARAMS, mcp_request


def test_a_real_token_is_accepted(client, token):
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS, token=token)
    assert response.status_code == 200, (
        "a token the auth server issued should be accepted (see the TODO in auth.py)"
    )


def test_no_token_is_still_rejected(client):
    assert mcp_request(client, "initialize", INITIALIZE_PARAMS).status_code == 401


def test_a_header_that_is_not_a_bearer_token_is_rejected(client):
    response = mcp_request(
        client, "initialize", INITIALIZE_PARAMS, headers={"Authorization": "Basic abc123"}
    )
    assert response.status_code == 401, (
        "only Bearer tokens count — a header alone is not authentication"
    )


def test_an_empty_bearer_is_rejected(client):
    response = mcp_request(
        client, "initialize", INITIALIZE_PARAMS, headers={"Authorization": "Bearer "}
    )
    assert response.status_code == 401


async def test_resolve_auth_info_reads_the_token(token):
    """The AuthInfo should carry what introspection said."""
    from auth import resolve_auth_info

    auth_info = await resolve_auth_info(f"Bearer {token}")

    assert auth_info is not None, "a valid token should resolve"
    assert auth_info.user_id == "user-kody", "`sub` from introspection is the user id"
    assert auth_info.token == token
    assert "entries:read" in auth_info.scopes, (
        "`scope` comes back space-separated and should end up as a list"
    )


async def test_no_header_resolves_to_none():
    from auth import resolve_auth_info

    assert await resolve_auth_info(None) is None
