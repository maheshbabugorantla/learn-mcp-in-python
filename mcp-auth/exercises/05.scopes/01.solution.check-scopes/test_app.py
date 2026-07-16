"""A tool only runs if the token is allowed to run it."""

from epicme.testing import call_tool, tool_text


def test_a_read_only_token_cannot_write(client, make_token):
    token = make_token("entries:read")
    result = call_tool(client, "create_entry", {"title": "nope", "content": "nope"}, token=token)

    assert result.get("isError"), (
        "creating an entry needs entries:write — this token hasn't got it "
        "(see the TODO in auth.py and server.py)"
    )
    assert "entries:write" in tool_text(result), (
        "say which scope was missing, so the model can explain itself"
    )


def test_a_read_only_token_can_read(client, make_token):
    token = make_token("entries:read")
    result = call_tool(client, "list_entries", token=token)
    assert not result.get("isError"), tool_text(result)


def test_a_write_token_can_write(client, make_token):
    token = make_token("entries:write")
    result = call_tool(client, "create_entry", {"title": "yes", "content": "yes"}, token=token)
    assert not result.get("isError"), tool_text(result)


def test_a_tool_needing_two_scopes_needs_both(client, make_token):
    """add_tag_to_entry wants entries:write *and* tags:read."""
    token = make_token("entries:write")
    result = call_tool(client, "add_tag_to_entry", {"entry_id": 1, "tag_id": 1}, token=token)
    assert result.get("isError"), "validate_scopes should require every scope, not any"
    assert "tags:read" in tool_text(result)


def test_whoami_needs_user_read(client, make_token):
    result = call_tool(client, "whoami", token=make_token("entries:read"))
    assert result.get("isError")
    assert "user:read" in tool_text(result)
