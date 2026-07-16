"""Scope hints: tell clients what they can ask for."""

from epicme.testing import call_tool, tool_text


def test_protected_resource_metadata_lists_supported_scopes(client):
    response = client.get("/.well-known/oauth-protected-resource/mcp")
    assert response.status_code == 200

    metadata = response.json()
    assert "scopes_supported" in metadata, (
        "`scopes_supported` is missing from the protected resource metadata — "
        "without it a client has to guess what to put in `scope=` (see the TODO "
        "in auth.py)."
    )
    assert set(metadata["scopes_supported"]) == {
        "user:read",
        "entries:read",
        "entries:write",
        "tags:read",
        "tags:write",
    }


def test_supported_scopes_are_the_ones_the_server_actually_checks(client):
    """The advertised list has to match reality, or clients ask for the wrong thing."""
    metadata = client.get("/.well-known/oauth-protected-resource/mcp").json()
    advertised = set(metadata["scopes_supported"])

    # Every advertised scope should be one the auth server will actually issue.
    from epicme.provider import SUPPORTED_SCOPES

    assert advertised <= set(SUPPORTED_SCOPES), (
        "the server advertises a scope its authorization server can't issue"
    )


def test_metadata_is_readable_without_a_token(client):
    """A client with no token is exactly who needs to read this."""
    assert client.get("/.well-known/oauth-protected-resource/mcp").status_code == 200


def test_a_scoped_token_still_works_end_to_end(client, make_token):
    token = make_token("entries:read")
    result = call_tool(client, "list_entries", token=token)
    assert "Found 2 entries" in tool_text(result)
