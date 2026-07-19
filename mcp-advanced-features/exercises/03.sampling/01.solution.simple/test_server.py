"""Sampling tests — a fake LLM answering the server's reflection request.

When the server calls `ctx.session.create_message(...)`, the client's LLM is what
answers. In a real client that's a live model; here the test supplies a
`sampling_callback` that returns fixed text, so we can assert the tool wove the
model's reply into its result. We also connect a client with *no* sampling
support to prove `create_entry` still works when nobody can answer.
"""

from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import CreateMessageResult, TextContent

from server import mcp


async def sampling_cb(context, params):
    # `params.messages` holds what the server asked; a real client would run its
    # LLM over them. We just return a canned encouraging line.
    return CreateMessageResult(
        role="assistant",
        content=TextContent(type="text", text="Keep it up!"),
        model="fake-model",
        stopReason="endTurn",
    )


async def test_reflection_is_appended_when_the_client_can_sample():
    async with connect(mcp, sampling_callback=sampling_cb) as client:
        result = await client.call_tool(
            "create_entry", {"title": "A good day", "content": "Everything clicked."}
        )
    assert not result.isError
    texts = " ".join(b.text for b in result.content if isinstance(b, TextContent))
    assert "Keep it up!" in texts, (
        f"🚨 the model's reflection should be appended to the result. Got: {texts!r}"
    )


async def test_create_entry_still_works_without_a_sampling_client():
    # No sampling_callback: the client can't answer create_message, so the server
    # must skip the reflection gracefully and still create the entry.
    async with connect(mcp) as client:
        result = await client.call_tool(
            "create_entry", {"title": "No LLM here", "content": "Should still save."}
        )
    assert not result.isError, "🚨 create_entry must succeed even without sampling support"
    texts = " ".join(b.text for b in result.content if isinstance(b, TextContent))
    assert "Created entry" in texts, (
        f"🚨 the entry should still be created without a sampling client. Got: {texts!r}"
    )
