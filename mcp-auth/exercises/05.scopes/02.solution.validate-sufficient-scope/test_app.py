"""A token that can do nothing here doesn't get in the door."""

from epicme.testing import INITIALIZE_PARAMS, mcp_request


def test_a_token_with_no_useful_scopes_is_forbidden(client, make_token):
    # `make_token` with an unknown scope: valid token, nothing we understand
    token = make_token("something:else")
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS, token=token)

    assert response.status_code == 403, (
        "a valid token carrying none of our scopes should be turned away once, at the "
        "door, rather than failing in every tool (see the TODO in app.py)"
    )


def test_the_403_explains_what_would_work(client, make_token):
    response = mcp_request(
        client, "initialize", INITIALIZE_PARAMS, token=make_token("something:else")
    )
    header = response.headers.get("WWW-Authenticate", "")

    assert 'error="insufficient_scope"' in header, f"got: {header}"
    assert "error_description=" in header
    for scope in (
        "user:read",
        "entries:read",
        "entries:write",
        "tags:read",
        "tags:write",
    ):
        assert scope in header, (
            f"the description should list {scope} as one of the combinations that work"
        )


def test_403_not_401(client, make_token):
    """401 means "go get a token" — this client has one, and refreshing won't help."""
    response = mcp_request(
        client, "initialize", INITIALIZE_PARAMS, token=make_token("something:else")
    )
    assert response.status_code != 401, (
        "sending a 401 here puts the client in a refresh loop against an "
        "authorization server that's behaving perfectly"
    )


def test_one_useful_scope_is_enough_to_get_in(client, make_token):
    response = mcp_request(
        client, "initialize", INITIALIZE_PARAMS, token=make_token("entries:read")
    )
    assert response.status_code == 200, (
        "any one of our scopes makes some part of the journal usable"
    )


def test_a_bad_token_is_still_a_401(client):
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS, token="not-a-token")
    assert response.status_code == 401, "don't confuse 'who?' with 'not allowed'"
