"""The 401 points at the instructions."""

from epicme.testing import INITIALIZE_PARAMS, mcp_request


def test_the_401_points_at_the_resource_metadata(client):
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS)
    header = response.headers.get("WWW-Authenticate", "")

    assert "resource_metadata=" in header, (
        "the 401 should carry a resource_metadata auth param so a client that has "
        "never seen this server can find its way in (see the TODO in auth.py)"
    )
    assert "/.well-known/oauth-protected-resource/mcp" in header, (
        f"resource_metadata should point at the protected resource metadata: {header}"
    )
    assert 'Bearer realm="EpicMe"' in header, "don't lose the realm"


def test_the_url_it_points_at_actually_serves_the_metadata(client):
    """A pointer to a 404 is worse than no pointer."""
    response = mcp_request(client, "initialize", INITIALIZE_PARAMS)
    header = response.headers.get("WWW-Authenticate", "")

    url = header.split("resource_metadata=")[1].split(",")[0].strip().strip('"')
    metadata = client.get(url)
    assert metadata.status_code == 200
    assert "authorization_servers" in metadata.json()
