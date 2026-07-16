"""Authorization server metadata."""

from epicme.auth_server import AUTH_SERVER_URL


def test_authorization_server_metadata_is_served(client):
    response = client.get("/.well-known/oauth-authorization-server")
    assert response.status_code == 200, (
        "this should forward the auth server's metadata (see the TODO in auth.py)"
    )

    metadata = response.json()
    for key in ("issuer", "authorization_endpoint", "token_endpoint"):
        assert key in metadata, f"the metadata should include {key}"

    assert metadata["issuer"].rstrip("/") == AUTH_SERVER_URL.rstrip("/")


def test_it_is_the_auth_servers_own_document(client):
    """We forward it; we don't invent it."""
    from epicme.auth_server import auth_app
    from starlette.testclient import TestClient

    with TestClient(auth_app) as auth_client:
        original = auth_client.get("/.well-known/oauth-authorization-server").json()

    assert client.get("/.well-known/oauth-authorization-server").json() == original


def test_metadata_still_has_cors_headers(client):
    response = client.get("/.well-known/oauth-authorization-server")
    assert response.headers.get("Access-Control-Allow-Origin") == "*"
