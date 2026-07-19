"""Sampling tests — a fake LLM whose suggestion drives a real DB change.

The server asks the client's LLM to name tags for a new entry. Our fake
`sampling_callback` returns "work, ideas"; the tool must parse that, create any
missing tags, and attach them to the entry. "work" already exists in the seed, so
this also checks the find-or-create path doesn't trip the unique-name constraint.
"""

from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import CreateMessageResult, TextContent

from server import db, mcp


async def sampling_cb(context, params):
    # A real client would run its LLM over params.messages; we return canned tags.
    return CreateMessageResult(
        role="assistant",
        content=TextContent(type="text", text="work, ideas"),
        model="fake-model",
        stopReason="endTurn",
    )


async def test_suggested_tags_are_created_and_attached():
    async with connect(mcp, sampling_callback=sampling_cb) as client:
        result = await client.call_tool(
            "create_entry", {"title": "Planning the roadmap", "content": "Sketched next quarter."}
        )
    assert not result.isError

    # The tag "ideas" didn't exist in the seed; it should now.
    tag_names = {t.name for t in db.get_tags()}
    assert "ideas" in tag_names, f"🚨 a suggested tag should be created. Tags: {tag_names}"

    # Both suggested tags should be attached to the entry we just created.
    entry = db.get_entries()[-1]
    attached = {t.name for t in entry.tags}
    assert {"work", "ideas"} <= attached, (
        f"🚨 the suggested tags should be attached to the new entry. Attached: {attached}"
    )
