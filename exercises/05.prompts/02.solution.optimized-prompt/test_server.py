import json

from mcp.shared.exceptions import McpError
from mcp.shared.memory import create_connected_server_and_client_session as connect

from server import mcp

RENDER_FAILED = (
    "Rendering the `suggest_tags` prompt failed: {error}. Check the TODO in server.py."
)


async def _get_prompt(name: str, arguments: dict[str, str]):
    """Fetch a rendered prompt, returning the McpError rather than raising it.

    Assertions belong *outside* `connect(...)` — one raised inside gets wrapped
    in an ExceptionGroup and the message you want to read ends up buried.
    """
    async with connect(mcp) as client:
        try:
            result = await client.get_prompt(name, arguments)
        except McpError as error:
            return error
    return result


async def _resources_in(entry_id: str = "1"):
    result = await _get_prompt("suggest_tags", {"entry_id": entry_id})
    if isinstance(result, McpError):
        raise AssertionError(RENDER_FAILED.format(error=result))
    return result, [m for m in result.messages if m.content.type == "resource"]


async def test_prompt_still_renders():
    """Whatever else changed, the prompt must still produce messages."""
    result, _ = await _resources_in()

    assert result.messages, "Rendering `suggest_tags` produced no messages."
    assert result.messages[0].content.type == "text", (
        "The first message should still be the text instructions telling the "
        f"model what to do. Got: {result.messages[0].content.type}"
    )


async def test_prompt_carries_the_data_with_it():
    """The point of this step: send the data, don't ask the model to fetch it."""
    _, resources = await _resources_in()

    assert resources, (
        "None of the messages carry a resource — the prompt is still just "
        "*asking* the model to go look things up. Embed the entry and the tag "
        "list in the messages (see the TODO in server.py)."
    )
    assert len(resources) >= 2, (
        "Expected two embedded resources: the entry itself and the list of "
        f"available tags. Got {len(resources)}."
    )


async def test_the_entry_is_embedded():
    """The model should receive the entry, already read, with its URI attached."""
    _, resources = await _resources_in()
    uris = [str(r.content.resource.uri) for r in resources]

    assert "epicme://entries/1" in uris, (
        "No message carries `epicme://entries/1`. Embed the entry you looked "
        f"up, using its own URI so the model knows what it's reading. Got: {uris}"
    )

    entry = next(r for r in resources if str(r.content.resource.uri) == "epicme://entries/1")
    assert entry.content.resource.mimeType == "application/json", (
        "Label the embedded entry `mimeType='application/json'` — it's JSON, "
        f"and the client shouldn't have to guess. Got: {entry.content.resource.mimeType}"
    )

    payload = json.loads(entry.content.resource.text)
    assert payload["title"] == "A quiet morning", (
        f"The embedded resource should hold the real entry. Got: {payload}"
    )


async def test_the_available_tags_are_embedded():
    """Suggesting tags means knowing which ones already exist."""
    _, resources = await _resources_in()
    uris = [str(r.content.resource.uri) for r in resources]

    assert "epicme://tags" in uris, (
        "No message carries `epicme://tags`. The model can't suggest existing "
        f"tags without being told which exist. Got: {uris}"
    )

    tags = next(r for r in resources if str(r.content.resource.uri) == "epicme://tags")
    names = [t["name"] for t in json.loads(tags.content.resource.text)]
    assert "home" in names, (
        f"The embedded tag list should hold the real tags. Got: {names}"
    )


async def test_unknown_entry_is_an_error():
    """Fetching in the prompt means it can now fail — say so clearly."""
    result = await _get_prompt("suggest_tags", {"entry_id": "999"})

    assert isinstance(result, McpError), (
        "Asking for entry 999 should fail — the prompt now looks the entry up, "
        "so raise a ValueError when it isn't there (see the TODO)."
    )
