"""Tool-annotation tests — the client reads each tool's advisory hints.

A client learns about a server's tools through `list_tools()`. Each tool can
carry `annotations` — a human title plus a set of behavioural hints
(readOnlyHint, destructiveHint, idempotentHint, openWorldHint). We list the
tools and check the hints that matter landed on the right tools.
"""

from mcp.shared.memory import create_connected_server_and_client_session as connect

from server import mcp


async def _tools_by_name():
    async with connect(mcp) as client:
        result = await client.list_tools()
    return {t.name: t for t in result.tools}


async def test_read_tool_is_marked_read_only():
    tools = await _tools_by_name()
    get_entry = tools["get_entry"]
    assert get_entry.annotations is not None and get_entry.annotations.readOnlyHint is True, (
        "🚨 get_entry only reads — annotate it with readOnlyHint=True so a client "
        "knows it's safe to call freely"
    )


async def test_delete_tool_is_marked_destructive():
    tools = await _tools_by_name()
    delete_tag = tools["delete_tag"]
    assert delete_tag.annotations is not None and delete_tag.annotations.destructiveHint is True, (
        "🚨 delete_tag removes data for good — annotate it with destructiveHint=True"
    )


async def test_update_tool_is_marked_idempotent():
    tools = await _tools_by_name()
    update_tag = tools["update_tag"]
    assert update_tag.annotations is not None and update_tag.annotations.idempotentHint is True, (
        "🚨 update_tag lands the same result if repeated — annotate it with idempotentHint=True"
    )
