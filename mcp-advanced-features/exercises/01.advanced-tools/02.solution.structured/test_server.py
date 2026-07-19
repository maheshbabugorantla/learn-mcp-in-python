"""Structured-output tests — the client gets data, not just a text blob.

When a tool declares a pydantic return type, FastMCP answers with two things:
`result.structuredContent` (the data as a validated dict) and a text-fallback
block. We call get_entry and get_tag and check both halves are there and that
the structured data matches what's in the database.
"""

from mcp.shared.memory import create_connected_server_and_client_session as connect

from server import db, mcp


async def test_get_entry_returns_structured_content():
    entry = db.get_entry(1)
    assert entry is not None
    expected = {"id": entry.id, "title": entry.title, "content": entry.content, "mood": entry.mood}

    async with connect(mcp) as client:
        result = await client.call_tool("get_entry", {"id": 1})

    assert result.structuredContent is not None and result.structuredContent == expected, (
        "🚨 get_entry should return a pydantic model so the client gets "
        f"structuredContent. Expected {expected!r}, got {result.structuredContent!r}"
    )
    # FastMCP also fills a text-fallback block for text-only clients.
    assert result.content and result.content[0].text, (
        "🚨 there should still be a text-fallback block alongside the structured data"
    )


async def test_get_tag_returns_structured_content():
    tag = db.get_tag(1)
    assert tag is not None
    expected = {"id": tag.id, "name": tag.name, "description": tag.description}

    async with connect(mcp) as client:
        result = await client.call_tool("get_tag", {"id": 1})

    assert result.structuredContent is not None and result.structuredContent == expected, (
        "🚨 get_tag should return a pydantic model so the client gets "
        f"structuredContent. Expected {expected!r}, got {result.structuredContent!r}"
    )
    assert result.content and result.content[0].text, (
        "🚨 there should still be a text-fallback block alongside the structured data"
    )
