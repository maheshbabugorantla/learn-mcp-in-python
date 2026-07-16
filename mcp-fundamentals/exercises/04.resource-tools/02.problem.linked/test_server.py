import json

from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import EmbeddedResource, ResourceLink, TextContent

from server import mcp

NO_LINKS = (
    "`list_entries` came back with text and nothing else — no ResourceLink in "
    "`result.content`. Build one link per entry in `list_entries()` in "
    "server.py (see the TODO). Got: {content}"
)


async def _call(name: str, args: dict):
    """Call a tool and hand the result back outside the session.

    Assertions belong *outside* `connect(...)` — one raised inside gets wrapped
    in an ExceptionGroup and the message you want to read ends up buried.
    """
    async with connect(mcp) as client:
        return await client.call_tool(name, args)


def _links(result):
    """The resource links in a tool result, if any."""
    return [c for c in result.content if isinstance(c, ResourceLink)]


async def test_list_entries_returns_links():
    """One link per entry, addressed the way the template expects."""
    result = await _call("list_entries", {})

    assert not result.isError, f"list_entries errored: {result.content}"

    links = _links(result)
    assert links, NO_LINKS.format(content=result.content)

    # The journal is seeded with two entries, and other tests may add more —
    # so check the seeded ones are linked rather than counting.
    # `uri` is an AnyUrl, so compare the string form — AnyUrl != str.
    uris = [str(link.uri) for link in links]
    for expected in ("epicme://entries/1", "epicme://entries/2"):
        assert expected in uris, (
            f"Expected a link to {expected} — build each URI as "
            f'f"epicme://entries/{{entry.id}}" from `db.get_entries()`. Got: {uris}'
        )


async def test_links_are_labelled_for_a_human():
    """A bare URI is unpickable — the title is what makes a link usable."""
    result = await _call("list_entries", {})

    links = _links(result)
    assert links, NO_LINKS.format(content=result.content)

    by_uri = {str(link.uri): link for link in links}
    first = by_uri["epicme://entries/1"]

    assert first.title == "A quiet morning", (
        "Set `title=entry.title` so the link says what it points at. "
        f"Got: {first.title!r}"
    )
    assert first.name, (
        "`name` is required on a ResourceLink — a short handle like "
        f'f"entry-{{entry.id}}" works. Got: {first.name!r}'
    )
    assert first.mimeType == "application/json", (
        "Set `mimeType=\"application/json\"` so a client knows what it would "
        f"be fetching. Got: {first.mimeType}"
    )


async def test_list_does_not_embed_the_entries():
    """The whole point: the list stays cheap. Contents stay on the server."""
    result = await _call("list_entries", {})

    embedded = [c for c in result.content if isinstance(c, EmbeddedResource)]
    assert not embedded, (
        "`list_entries` should return links, not embedded resources — a list "
        "that inlines every entry is exactly the cost we're avoiding. Use "
        "ResourceLink here and leave the embedding to `get_entry`."
    )

    text = " ".join(c.text for c in result.content if isinstance(c, TextContent))
    assert "watched the fog burn off the hills" not in text, (
        "The body of an entry leaked into the text block. A link carries the "
        "address, not the contents."
    )


async def test_list_leads_with_a_summary():
    """Links are for the client; the sentence is for whoever's reading along."""
    result = await _call("list_entries", {})

    assert result.content, "list_entries returned no content at all."
    assert isinstance(result.content[0], TextContent), (
        "Keep the TextContent summary first, with the links after it. "
        f"Got: {type(result.content[0]).__name__}"
    )


async def test_new_entries_show_up_in_the_list():
    """The list is built from the db on every call, not from a snapshot."""
    before = _links(await _call("list_entries", {}))
    assert before, NO_LINKS.format(content="(none)")

    created = await _call(
        "create_entry",
        {"title": "A new leaf", "content": "Wrote it down for once.", "mood": "hopeful"},
    )
    assert not created.isError, f"create_entry errored: {created.content}"

    # create_entry embeds the record, so the new id arrives with it — no
    # second round-trip needed. That's step 1 paying off.
    embedded = [c for c in created.content if isinstance(c, EmbeddedResource)]
    assert embedded, (
        "create_entry should still embed the entry it created (from step 1). "
        f"Got: {created.content}"
    )
    new_id = json.loads(embedded[0].resource.text)["id"]

    after = _links(await _call("list_entries", {}))
    uris = [str(link.uri) for link in after]
    assert f"epicme://entries/{new_id}" in uris, (
        "The new entry should appear in the next `list_entries` — read from "
        f"`db.get_entries()` each call. Got: {uris}"
    )
    assert len(after) == len(before) + 1, (
        f"Expected exactly one new link. Before: {len(before)}, after: {len(after)}"
    )


async def test_links_can_be_followed():
    """A link is a promise: the URI it names has to actually be readable."""
    result = await _call("list_entries", {})

    links = _links(result)
    assert links, NO_LINKS.format(content=result.content)

    async with connect(mcp) as client:
        read = await client.read_resource(links[0].uri)

    entry = json.loads(read.contents[0].text)
    assert entry["id"] == 1, (
        "Following the first link should land on entry 1 — the link's URI has "
        f"to match what the `epicme://entries/{{id}}` template serves. Got: {entry}"
    )
