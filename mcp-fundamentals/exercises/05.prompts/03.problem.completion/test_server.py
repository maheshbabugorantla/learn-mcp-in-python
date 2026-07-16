from mcp.shared.exceptions import McpError
from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import PromptReference, ResourceTemplateReference

from server import mcp

NO_HANDLER = (
    "The completion request failed: {error}. A server only advertises "
    "completion support once a handler exists — register one with "
    "`@mcp.completion()` in server.py."
)


async def _complete(ref, name: str, value: str):
    """Ask for completions, returning the McpError rather than raising it.

    Assertions belong *outside* `connect(...)` — one raised inside gets wrapped
    in an ExceptionGroup and the message you want to read ends up buried.
    """
    async with connect(mcp) as client:
        try:
            result = await client.complete(ref, {"name": name, "value": value})
        except McpError as error:
            return error
    return result


async def _values(ref, name: str, value: str) -> list[str]:
    result = await _complete(ref, name, value)
    if isinstance(result, McpError):
        raise AssertionError(NO_HANDLER.format(error=result))
    return result.completion.values


async def test_prompt_argument_is_completed():
    """Picking `suggest_tags` should suggest entry ids that actually exist."""
    values = await _values(
        PromptReference(type="ref/prompt", name="suggest_tags"), "entry_id", ""
    )

    assert values, (
        "No completions for the `suggest_tags` prompt's `entry_id` argument — "
        "a user has to know the id by heart. Add a PromptReference branch to "
        "the completion handler (see the TODO in server.py)."
    )
    assert "1" in values and "2" in values, (
        "The seeded journal has entries 1 and 2, so an empty value should "
        f"offer both. Suggest real ids from the database. Got: {values}"
    )


async def test_prompt_completions_are_filtered():
    """Completion narrows as the user types — that's the whole point."""
    values = await _values(
        PromptReference(type="ref/prompt", name="suggest_tags"), "entry_id", "2"
    )

    assert values == ["2"], (
        "Typing '2' should narrow the suggestions to ids starting with '2'. "
        f"Filter on `argument.value`. Got: {values}"
    )


async def test_unknown_prompt_argument_gets_no_suggestions():
    """A ref you don't recognise deserves None, not a crash."""
    result = await _complete(
        PromptReference(type="ref/prompt", name="suggest_tags"), "nonsense", ""
    )

    assert not isinstance(result, McpError), (
        f"Completing an unknown argument should return no suggestions, not "
        f"fail: {result}"
    )
    assert result.completion.values == [], (
        f"An argument you don't handle should get no suggestions. Got: "
        f"{result.completion.values}"
    )


async def test_resource_template_completion_still_works():
    """The step before this one must keep working."""
    values = await _values(
        ResourceTemplateReference(
            type="ref/resource", uri="epicme://entries/{id}"
        ),
        "id",
        "",
    )

    assert "1" in values, (
        "Completing `epicme://entries/{id}` stopped working — the template "
        f"branch of the handler should still answer. Got: {values}"
    )


async def test_tag_template_completion_still_works():
    """And so must the tag template."""
    values = await _values(
        ResourceTemplateReference(type="ref/resource", uri="epicme://tags/{id}"),
        "id",
        "",
    )

    assert "1" in values, (
        f"Completing `epicme://tags/{{id}}` stopped working. Got: {values}"
    )
