import json

from mcp.shared.exceptions import McpError
from mcp.shared.memory import create_connected_server_and_client_session as connect
from pydantic import AnyUrl

from server import mcp

MISSING = (
    "No `epicme://tags` resource is registered — add it in server.py "
    "(see the TODO). Resources found: {found}"
)


async def test_tags_resource_is_listed():
    """A client should be able to discover `epicme://tags` via resources/list."""
    async with connect(mcp) as client:
        result = await client.list_resources()

    uris = [str(resource.uri) for resource in result.resources]
    assert "epicme://tags" in uris, MISSING.format(found=uris)


async def test_tags_resource_describes_itself():
    """The description and mime type are what a client shows and trusts."""
    async with connect(mcp) as client:
        result = await client.list_resources()

    uris = [str(resource.uri) for resource in result.resources]
    assert "epicme://tags" in uris, MISSING.format(found=uris)

    tags = next(r for r in result.resources if str(r.uri) == "epicme://tags")
    assert tags.mimeType == "application/json", (
        'Pass `mime_type="application/json"` to @mcp.resource so clients know '
        f"this is JSON. Got: {tags.mimeType!r}"
    )
    assert tags.description, (
        "Give the resource a `description` — it's what a user sees in a picker UI."
    )


async def test_tags_resource_returns_the_tags():
    """Reading the resource should give back every tag as JSON."""
    # Read inside the session, but assert outside it: an assertion that fires
    # inside `connect(...)` gets wrapped in an ExceptionGroup and the message
    # you actually want to read ends up buried in a traceback.
    async with connect(mcp) as client:
        try:
            result = await client.read_resource(AnyUrl("epicme://tags"))
        except McpError as error:
            result = error

    if isinstance(result, McpError):
        raise AssertionError(
            f"Reading `epicme://tags` failed: {result}. {MISSING.format(found='none')}"
        )

    assert result.contents, "Reading `epicme://tags` returned no contents at all."

    tags = json.loads(result.contents[0].text)
    assert isinstance(tags, list), (
        f"Expected a JSON array of tags. Got {type(tags).__name__}: {tags!r}"
    )

    # The seeded journal has these three tags.
    names = sorted(tag["name"] for tag in tags)
    assert names == ["home", "travel", "work"], (
        "Expected every tag from `db.get_tags()`, serialized with `.to_dict()`. "
        f"Got: {names}"
    )
