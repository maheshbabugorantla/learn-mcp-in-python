"""Say *why* the 401 happened — but only when you know."""

from epicme.testing import INITIALIZE_PARAMS, mcp_request


def test_a_bad_token_gets_an_error_auth_param(client):
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS, token="not-a-token")
    header = response.headers.get("WWW-Authenticate", "")

    assert 'error="invalid_token"' in header, (
        "when a token was sent and it's no good, say so (see the TODO in auth.py)"
    )
    assert "error_description=" in header, (
        "a human-readable explanation belongs alongside the error code"
    )


def test_no_token_gets_no_error_auth_param(client):
    """Nothing was invalid — there was nothing."""
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS)
    header = response.headers.get("WWW-Authenticate", "")

    assert 'error="invalid_token"' not in header, (
        "don't tell a client its nonexistent token is invalid — it'll go off and try "
        "to refresh something it hasn't got"
    )
    assert 'Bearer realm="EpicMe"' in header
    assert "resource_metadata=" in header


def test_both_kinds_of_401_still_point_at_the_metadata(client):
    for token in (None, "not-a-token"):
        header = mcp_request(
            client, "initialize", INITIALIZE_PARAMS, token=token
        ).headers.get("WWW-Authenticate", "")
        assert "resource_metadata=" in header
