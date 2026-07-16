from mcp.shared.exceptions import McpError
from mcp.shared.memory import create_connected_server_and_client_session as connect

from server import mcp

MISSING = (
    "The server doesn't advertise a `suggest_tags` prompt. Register one with "
    "`@mcp.prompt()` in server.py (see the TODO). Found: {found}"
)

RENDER_FAILED = (
    "Rendering the `suggest_tags` prompt failed: {error}. Register it with "
    "`@mcp.prompt()` in server.py (see the TODO)."
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


async def _list_prompts():
    async with connect(mcp) as client:
        result = await client.list_prompts()
    return result.prompts


async def test_prompt_is_listed():
    """A prompt only exists for a user if the server tells them about it."""
    prompts = await _list_prompts()
    names = [p.name for p in prompts]

    assert "suggest_tags" in names, MISSING.format(found=names or "no prompts at all")


async def test_prompt_has_a_description():
    """The description is the label a person reads before picking it."""
    prompts = await _list_prompts()
    prompt = next((p for p in prompts if p.name == "suggest_tags"), None)

    assert prompt is not None, MISSING.format(found=[p.name for p in prompts])
    assert prompt.description, (
        "Give the prompt a `description=` — it's what the human sees in the "
        "menu, so it should read like a menu item, not a function name."
    )


async def test_prompt_declares_its_entry_id_argument():
    """The client builds its input form from this list."""
    prompts = await _list_prompts()
    prompt = next((p for p in prompts if p.name == "suggest_tags"), None)

    assert prompt is not None, MISSING.format(found=[p.name for p in prompts])

    arguments = prompt.arguments or []
    names = [a.name for a in arguments]
    assert "entry_id" in names, (
        "The prompt should take an `entry_id` argument — FastMCP builds this "
        f"list from your function's parameters. Got: {names}"
    )

    entry_id = next(a for a in arguments if a.name == "entry_id")
    assert entry_id.required, (
        "`entry_id` should be required — a parameter with no default is."
    )
    assert entry_id.description, (
        "Describe the argument with "
        "`Annotated[str, Field(description=...)]` so the client can label the "
        "input it shows the user."
    )


async def test_rendering_the_prompt_mentions_the_entry():
    """Rendering substitutes the argument into the message."""
    result = await _get_prompt("suggest_tags", {"entry_id": "1"})

    if isinstance(result, McpError):
        raise AssertionError(RENDER_FAILED.format(error=result))

    assert result.messages, (
        "Rendering `suggest_tags` produced no messages — the prompt function "
        "should return the text to send."
    )

    message = result.messages[0]
    assert message.role == "user", (
        f"A prompt returning a plain string becomes a user message. Got: {message.role}"
    )

    text = message.content.text
    assert "1" in text, (
        "The rendered prompt should mention the entry id it was given — "
        f"interpolate `entry_id` into the text. Got: {text!r}"
    )
    assert "tag" in text.lower(), (
        f"The prompt should actually ask about tags. Got: {text!r}"
    )


async def test_argument_is_a_string_on_the_wire():
    """Prompt arguments are always strings — a different id must flow through."""
    result = await _get_prompt("suggest_tags", {"entry_id": "2"})

    if isinstance(result, McpError):
        raise AssertionError(RENDER_FAILED.format(error=result))

    text = result.messages[0].content.text

    assert "2" in text, (
        "Rendering with `entry_id=\"2\"` should mention entry 2. Prompt "
        f"arguments arrive as strings, so take a `str`. Got: {text!r}"
    )
