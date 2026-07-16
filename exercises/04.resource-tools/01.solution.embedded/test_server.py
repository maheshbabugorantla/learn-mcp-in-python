import json

from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import EmbeddedResource, TextContent, TextResourceContents

from server import mcp

NO_EMBED = (
    "The tool came back with text and nothing else — no EmbeddedResource in "
    "`result.content`. Add the entry to the content list in `entry_result()` "
    "in server.py (see the TODO). Got: {content}"
)


async def _call(name: str, args: dict):
    """Call a tool and hand the result back outside the session.

    Assertions belong *outside* `connect(...)` — one raised inside gets wrapped
    in an ExceptionGroup and the message you want to read ends up buried.
    """
    async with connect(mcp) as client:
        return await client.call_tool(name, args)


def _embedded(result):
    """The embedded resources in a tool result, if any."""
    return [c for c in result.content if isinstance(c, EmbeddedResource)]


async def test_get_entry_embeds_the_entry():
    """Reading entry 1 should hand back the record, not a description of it."""
    result = await _call("get_entry", {"id": 1})

    assert not result.isError, f"get_entry(1) errored: {result.content}"

    embedded = _embedded(result)
    assert embedded, NO_EMBED.format(content=result.content)

    resource = embedded[0].resource
    assert isinstance(resource, TextResourceContents), (
        "The entry is JSON, so it belongs in a `TextResourceContents`. "
        f"Got: {type(resource).__name__}"
    )

    # The seeded journal's first entry never changes.
    entry = json.loads(resource.text)
    assert entry["title"] == "A quiet morning", (
        "Expected the embedded text to be the entry serialized with "
        f"`json.dumps(entry.to_dict(), indent=2)`. Got: {resource.text!r}"
    )
    assert entry["id"] == 1, f"Expected entry 1, got: {entry.get('id')}"


async def test_embedded_resource_points_at_the_entry_uri():
    """The embedded resource carries the URI it would have been read from."""
    result = await _call("get_entry", {"id": 1})

    embedded = _embedded(result)
    assert embedded, NO_EMBED.format(content=result.content)

    # `uri` is an AnyUrl, so compare the string form — AnyUrl != str.
    assert str(embedded[0].resource.uri) == "epicme://entries/1", (
        "Use the same URI the `epicme://entries/{id}` template serves: "
        f'f"epicme://entries/{{entry.id}}". Got: {embedded[0].resource.uri}'
    )


async def test_embedded_resource_is_json():
    """Say what the payload is so a client doesn't have to sniff it."""
    result = await _call("get_entry", {"id": 1})

    embedded = _embedded(result)
    assert embedded, NO_EMBED.format(content=result.content)

    assert embedded[0].resource.mimeType == "application/json", (
        "Set `mimeType=\"application/json\"` on the TextResourceContents. "
        f"Got: {embedded[0].resource.mimeType}"
    )


async def test_result_still_leads_with_text():
    """A human reads the transcript too — keep the sentence, add the data."""
    result = await _call("get_entry", {"id": 1})

    assert result.content, "get_entry returned no content at all."
    assert isinstance(result.content[0], TextContent), (
        "Keep the TextContent summary as the first block, with the "
        f"EmbeddedResource after it. Got: {type(result.content[0]).__name__}"
    )
    assert "A quiet morning" in result.content[0].text, (
        f"Expected the summary to name the entry. Got: {result.content[0].text!r}"
    )


async def test_create_entry_embeds_what_it_created():
    """The same helper serves create_entry, so it gets the record back too."""
    result = await _call(
        "create_entry",
        {"title": "Learning MCP", "content": "Tools can return resources.", "mood": "curious"},
    )

    assert not result.isError, f"create_entry errored: {result.content}"

    embedded = _embedded(result)
    assert embedded, NO_EMBED.format(content=result.content)

    entry = json.loads(embedded[0].resource.text)
    assert entry["title"] == "Learning MCP", (
        f"Expected the entry that was just created. Got: {entry}"
    )
    # The id is assigned by the database, and this is why embedding pays off:
    # the caller learns it without a second round-trip.
    assert entry["id"], "The created entry should carry the id the db assigned."
    assert str(embedded[0].resource.uri) == f"epicme://entries/{entry['id']}", (
        "The URI should be built from the *created* entry's id. "
        f"Got: {embedded[0].resource.uri}"
    )


async def test_missing_entry_is_still_an_error():
    """Errors work the way they did in 02.tools — nothing here changes that."""
    result = await _call("get_entry", {"id": 99999})

    assert result.isError, (
        "Reading an entry that doesn't exist should be an error result. "
        "`raise ValueError(...)` when `db.get_entry(id)` returns None."
    )
