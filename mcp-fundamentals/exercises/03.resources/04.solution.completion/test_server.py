from mcp.shared.exceptions import McpError
from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import ResourceTemplateReference

from server import mcp

NO_HANDLER = (
    "The completion request failed: {error}. A server only advertises "
    "completion support once a handler exists — register one with "
    "`@mcp.completion()` in server.py (see the TODO)."
)


async def _complete(uri: str, name: str = "id", value: str = ""):
    """Ask for completions, returning the McpError rather than raising it.

    Assertions belong *outside* `connect(...)` — one raised inside gets wrapped
    in an ExceptionGroup and the message you want to read ends up buried.
    """
    ref = ResourceTemplateReference(type="ref/resource", uri=uri)
    async with connect(mcp) as client:
        try:
            result = await client.complete(ref, {"name": name, "value": value})
        except McpError as error:
            return error
    return result.completion


async def test_completes_tag_ids():
    """An empty value should suggest every tag id."""
    completion = await _complete("epicme://tags/{id}")

    if isinstance(completion, McpError):
        raise AssertionError(NO_HANDLER.format(error=completion))

    # The seeded journal has three tags: home, work, travel.
    assert completion.values == ["1", "2", "3"], (
        "Expected an id from `db.get_tags()` for each tag, as strings. "
        f"Got: {completion.values}"
    )


async def test_completes_entry_ids():
    """The same handler has to route the other template to entries."""
    completion = await _complete("epicme://entries/{id}")

    if isinstance(completion, McpError):
        raise AssertionError(NO_HANDLER.format(error=completion))

    assert completion.values == ["1", "2"], (
        "Expected an id from `db.get_entries()` for each entry — dispatch on "
        f"`ref.uri` to pick the right table. Got: {completion.values}"
    )


async def test_filters_by_what_is_typed():
    """A user who typed `2` shouldn't be offered `1`."""
    completion = await _complete("epicme://tags/{id}", value="2")

    if isinstance(completion, McpError):
        raise AssertionError(NO_HANDLER.format(error=completion))

    assert completion.values == ["2"], (
        "Filter the ids against `argument.value` with `.startswith(...)`. "
        f"Got: {completion.values}"
    )


async def test_ignores_arguments_it_does_not_know():
    """The handler sees every completion request — decline the rest with None."""
    completion = await _complete("epicme://tags/{id}", name="nonsense")

    if isinstance(completion, McpError):
        raise AssertionError(NO_HANDLER.format(error=completion))

    assert completion.values == [], (
        "Return None unless `argument.name == \"id\"` — your handler is asked "
        f"about every argument on the server. Got: {completion.values}"
    )


async def test_ignores_unknown_templates():
    """A template you don't complete for should get nothing back."""
    completion = await _complete("epicme://unknown/{id}")

    if isinstance(completion, McpError):
        raise AssertionError(NO_HANDLER.format(error=completion))

    assert completion.values == [], (
        "Return None for template URIs you don't recognize. "
        f"Got: {completion.values}"
    )
