"""The journal belongs to whoever holds the token."""

import json

from epicme.testing import call_tool, tool_text


def _entry_id(result):
    payload = next(b for b in result["content"] if b["type"] == "resource")
    return json.loads(payload["resource"]["text"])["id"]


def test_each_token_sees_its_own_journal(client, token, other_token):
    kody = call_tool(client, "create_entry", {"title": "Kody only", "content": "mine"}, token=token)
    kody_id = _entry_id(kody)

    olivia = call_tool(
        client, "create_entry", {"title": "Olivia only", "content": "hers"}, token=other_token
    )
    olivia_id = _entry_id(olivia)

    assert kody_id != olivia_id

    # one user cannot read the other's entry, even knowing its id
    stolen = call_tool(client, "get_entry", {"id": olivia_id}, token=token)
    assert stolen.get("isError"), (
        "kody should not be able to read olivia's entry — is every db call passing "
        "the authenticated user's id? (see the TODO in app.py and server.py)"
    )
    assert "not found" in tool_text(stolen).lower()

    mine = call_tool(client, "get_entry", {"id": olivia_id}, token=other_token)
    assert not mine.get("isError"), "olivia should be able to read her own entry"


def test_entries_are_created_for_the_authenticated_user(client, other_token):
    created = call_tool(
        client, "create_entry", {"title": "Olivia's", "content": "hers"}, token=other_token
    )
    new_id = _entry_id(created)

    read_back = call_tool(client, "get_entry", {"id": new_id}, token=other_token)
    assert "Olivia's" in tool_text(read_back)
