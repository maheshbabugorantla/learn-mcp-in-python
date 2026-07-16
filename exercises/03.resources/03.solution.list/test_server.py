import json

from mcp.shared.exceptions import McpError
from mcp.shared.memory import create_connected_server_and_client_session as connect
from pydantic import AnyUrl

from server import mcp

MISSING = (
    "No `epicme://entries` collection resource is registered — add it in "
    "server.py (see the TODO). Resources found: {found}"
)


async def test_entries_collection_is_listed():
    """The collection is what makes entries discoverable at all."""
    async with connect(mcp) as client:
        result = await client.list_resources()

    uris = [str(resource.uri) for resource in result.resources]
    assert "epicme://entries" in uris, MISSING.format(found=uris)


async def test_templates_are_not_in_resources_list():
    """The reason the collection has to exist.

    Python has no per-template `list` callback, so a template is only ever a
    pattern under resources/templates/list. Nothing here is something you fix —
    it documents the split this exercise is built around.
    """
    async with connect(mcp) as client:
        listed = await client.list_resources()
        templated = await client.list_resource_templates()

    uris = [str(resource.uri) for resource in listed.resources]
    assert not any("{id}" in uri for uri in uris), (
        f"Templates should never appear in resources/list. Found: {uris}"
    )

    patterns = [t.uriTemplate for t in templated.resourceTemplates]
    assert "epicme://entries/{id}" in patterns, (
        f"The entry template should still be listed as a pattern. Found: {patterns}"
    )


async def test_entries_collection_indexes_every_entry():
    """Each record should carry the URI that reads it."""
    async with connect(mcp) as client:
        try:
            result = await client.read_resource(AnyUrl("epicme://entries"))
        except McpError as error:
            result = error

    if isinstance(result, McpError):
        raise AssertionError(
            f"Reading `epicme://entries` failed: {result}. "
            + MISSING.format(found="none")
        )

    entries = json.loads(result.contents[0].text)
    assert isinstance(entries, list), (
        f"Expected a JSON array of entries. Got {type(entries).__name__}: {entries!r}"
    )
    assert len(entries) == 2, (
        f"The seeded journal has 2 entries — return all of them. Got: {entries!r}"
    )

    titles = [entry["title"] for entry in entries]
    assert titles == ["A quiet morning", "Shipped the thing"], (
        f"Expected every entry from `db.get_entries()`. Got: {titles}"
    )

    for entry in entries:
        assert entry.get("uri") == f"epicme://entries/{entry['id']}", (
            "Give each record a `uri` pointing at its template URI, so a client "
            "can follow the index straight to the full entry. Got: "
            f"{entry.get('uri')!r} for entry {entry['id']}"
        )


async def test_collection_uris_are_actually_readable():
    """Walk the index like a client would: list, then follow a link."""
    async with connect(mcp) as client:
        try:
            listing = await client.read_resource(AnyUrl("epicme://entries"))
            entries = json.loads(listing.contents[0].text)
            followed = await client.read_resource(AnyUrl(entries[0]["uri"]))
        except (McpError, KeyError, IndexError) as error:
            followed = error

    if isinstance(followed, Exception):
        raise AssertionError(
            f"Following the first `uri` from `epicme://entries` failed: {followed}. "
            + MISSING.format(found="none")
        )

    entry = json.loads(followed.contents[0].text)
    assert entry["title"] == "A quiet morning", (
        f"The uri in the index should read back that entry. Got: {entry!r}"
    )
