"""Requests with no Authorization header get turned away."""

from epicme.testing import INITIALIZE_PARAMS, mcp_request


def test_no_authorization_header_is_rejected(client):
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS)
    assert response.status_code == 401, (
        "/mcp should reject a request with no Authorization header — is the MCP app "
        "wrapped in WithAuth? (see the TODO in app.py)"
    )


def test_the_401_says_how_to_authenticate(client):
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS)
    header = response.headers.get("WWW-Authenticate")

    assert header, "a 401 must carry a WWW-Authenticate header"
    assert 'Bearer realm="EpicMe"' in header, (
        f'expected Bearer realm="EpicMe", got: {header}'
    )


def test_a_request_with_a_header_gets_through(client, token):
    """We're not checking the token yet — only that one is present."""
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS, token=token)
    assert response.status_code == 200


def test_discovery_stays_public(client):
    assert client.get("/.well-known/oauth-protected-resource/mcp").status_code == 200
    assert client.get("/healthcheck").status_code == 200
