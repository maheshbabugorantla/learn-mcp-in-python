"""Elicitation tests — a fake user answering the server's confirmation prompt.

The test client supplies an `elicitation_callback`. When the server calls
`ctx.elicit(...)`, this callback is what answers — standing in for the human a
real client would prompt. We run the same delete twice: once with a user who
confirms, once with a user who declines, and check the tool did the right thing.
"""

from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import ElicitResult

from server import db, mcp


def make_elicit_callback(answer: bool):
    async def elicit(context, params):
        # `params.message` is the question the server asked; a real client would
        # show it to the user. We just answer with the fixed decision.
        return ElicitResult(action="accept", content={"confirmed": answer})

    return elicit


async def _delete_tag(answer: bool):
    async with connect(mcp, elicitation_callback=make_elicit_callback(answer)) as client:
        return await client.call_tool("delete_tag", {"id": 1})


async def test_confirmed_delete_removes_the_tag():
    assert db.get_tag(1) is not None
    result = await _delete_tag(answer=True)
    assert not result.isError
    text = result.content[0].text.lower()
    assert "deleted" in text, f"🚨 a confirmed delete should report success. Got: {text!r}"
    assert db.get_tag(1) is None, "🚨 the tag should be gone after a confirmed delete"


async def test_declined_delete_keeps_the_tag():
    # Re-seed since the previous test may have removed tag 1.
    if db.get_tag(1) is None:
        db.seed()
    tag = db.get_tags()[0]
    async with connect(mcp, elicitation_callback=make_elicit_callback(False)) as client:
        result = await client.call_tool("delete_tag", {"id": tag.id})
    assert not result.isError
    text = result.content[0].text.lower()
    assert "kept" in text or "declined" in text, (
        f"🚨 a declined delete should report the tag was kept. Got: {text!r}"
    )
    assert db.get_tag(tag.id) is not None, "🚨 the tag should still exist after a declined delete"
