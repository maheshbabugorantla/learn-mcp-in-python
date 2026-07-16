import json

from mcp.shared.exceptions import McpError
from mcp.shared.memory import create_connected_server_and_client_session as connect
from pydantic import AnyUrl

from server import mcp

MISSING = (
    "No `{template}` resource template is registered — add it in server.py "
    "(see the TODO). Templates found: {found}"
)


async def _read(uri: str):
    """Read a URI, returning the McpError instead of raising it.

    Assertions must happen *outside* `connect(...)`: one raised inside gets
    wrapped in an ExceptionGroup and the useful message ends up buried.
    """
    async with connect(mcp) as client:
        try:
            return await client.read_resource(AnyUrl(uri))
        except McpError as error:
            return error


async def test_templates_are_listed():
    """Templates show up under resources/templates/list — not resources/list."""
    async with connect(mcp) as client:
        result = await client.list_resource_templates()

    found = [t.uriTemplate for t in result.resourceTemplates]
    assert "epicme://tags/{id}" in found, MISSING.format(
        template="epicme://tags/{id}", found=found
    )
    assert "epicme://entries/{id}" in found, MISSING.format(
        template="epicme://entries/{id}", found=found
    )


async def test_read_a_single_tag():
    """`epicme://tags/1` should route to the template with id="1"."""
    result = await _read("epicme://tags/1")

    if isinstance(result, McpError):
        raise AssertionError(
            f"Reading `epicme://tags/1` failed: {result}. Register the "
            "`epicme://tags/{id}` template in server.py (see the TODO)."
        )

    tag = json.loads(result.contents[0].text)
    assert tag["id"] == 1, f"Expected the tag with id 1. Got: {tag!r}"
    assert tag["name"] == "home", (
        f"Expected the seeded 'home' tag from `db.get_tag(int(id))`. Got: {tag!r}"
    )


async def test_read_a_single_entry():
    """An entry's `.to_dict()` brings its tags along for free."""
    result = await _read("epicme://entries/1")

    if isinstance(result, McpError):
        raise AssertionError(
            f"Reading `epicme://entries/1` failed: {result}. Register the "
            "`epicme://entries/{id}` template in server.py (see the TODO)."
        )

    entry = json.loads(result.contents[0].text)
    assert entry["id"] == 1, f"Expected the entry with id 1. Got: {entry!r}"
    assert entry["title"] == "A quiet morning", (
        f"Expected the seeded entry from `db.get_entry(int(id))`. Got: {entry!r}"
    )
    assert [tag["name"] for tag in entry["tags"]] == ["home"], (
        "An entry's `.to_dict()` should include its tags. Got: "
        f"{entry.get('tags')!r}"
    )


async def test_missing_tag_is_an_error():
    """A read for a record that doesn't exist must fail loudly."""
    result = await _read("epicme://tags/999")

    assert isinstance(result, McpError), (
        "Reading `epicme://tags/999` should raise. `db.get_tag()` returns None "
        "for a missing tag — check for it and `raise ValueError(...)` rather "
        f"than returning it. Got back: {result!r}"
    )
    assert "not found" in str(result), (
        "Say the record wasn't found (and include the id) in the ValueError "
        f"message. Got: {result}"
    )


async def test_missing_entry_is_an_error():
    result = await _read("epicme://entries/999")

    assert isinstance(result, McpError), (
        "Reading `epicme://entries/999` should raise a ValueError from your "
        f"template. Got back: {result!r}"
    )
    assert "not found" in str(result), (
        f"Mention that the entry wasn't found in the error message. Got: {result}"
    )
