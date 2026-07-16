"""Protected resource metadata."""

from epicme.auth_server import AUTH_SERVER_URL


def test_protected_resource_metadata_is_served(client):
    response = client.get("/.well-known/oauth-protected-resource/mcp")
    assert response.status_code == 200, (
        "this should describe the resource server (see the TODO in auth.py)"
    )

    metadata = response.json()
    assert metadata["resource"].endswith("/mcp"), (
        "`resource` should be the URL of this server's MCP endpoint"
    )
    assert metadata["authorization_servers"] == [AUTH_SERVER_URL], (
        "`authorization_servers` should name the EpicMe authorization server"
    )


def test_resource_url_is_built_from_the_request(client):
    """Not hardcoded — the same code has to be right on localhost and in prod."""
    metadata = client.get("/.well-known/oauth-protected-resource/mcp").json()
    assert metadata["resource"] == "http://testserver/mcp"


def test_it_is_readable_without_a_token(client):
    """The client that needs this document is the one that hasn't got a token."""
    assert client.get("/.well-known/oauth-protected-resource/mcp").status_code == 200
