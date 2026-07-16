"""An inactive token is not a token."""

from epicme.auth_server import provider
from epicme.testing import INITIALIZE_PARAMS, mcp_request


def test_a_token_the_auth_server_never_issued_is_rejected(client):
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS, token="not-a-token")
    assert response.status_code == 401, (
        "introspection answers `{'active': false}` for a token it doesn't know — "
        "handle that branch instead of blowing up (see the TODO in auth.py)"
    )


def test_a_revoked_token_is_rejected(client, token):
    assert mcp_request(client, "initialize", INITIALIZE_PARAMS, token=token).status_code == 200

    # revoke it out from under the request
    provider.access_tokens.pop(token)

    response = mcp_request(client, "initialize", INITIALIZE_PARAMS, token=token)
    assert response.status_code == 401, (
        "a token that was valid a moment ago is no longer active"
    )


def test_a_live_token_still_works(client, token):
    assert mcp_request(client, "initialize", INITIALIZE_PARAMS, token=token).status_code == 200


async def test_resolve_auth_info_returns_none_for_an_inactive_token():
    from auth import resolve_auth_info

    assert await resolve_auth_info("Bearer nonsense") is None, (
        "an inactive introspection response should resolve to None, not raise"
    )
