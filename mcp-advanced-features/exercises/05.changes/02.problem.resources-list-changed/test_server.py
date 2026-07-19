"""resources/list_changed tests — watching a create invalidate the collection.

Same shape as the tools/list_changed test: a `message_handler` collects every
`ServerNotification` the server pushes. This time we create a tag (and an entry)
and check that a `ResourceListChangedNotification` arrives, since the
`epicme://tags` / `epicme://entries` collections just changed.
"""

import anyio
from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import ServerNotification

from server import mcp


async def test_create_tag_announces_the_resource_list_changed():
    notes: list[str] = []

    async def message_handler(message):
        if isinstance(message, ServerNotification):
            notes.append(type(message.root).__name__)

    async with connect(mcp, message_handler=message_handler) as client:
        await client.call_tool("create_tag", {"name": "sabbatical"})
        await anyio.sleep(0.1)

    assert "ResourceListChangedNotification" in notes, (
        "🚨 creating a tag changes the epicme://tags collection, so the server "
        "should send a ResourceListChangedNotification. "
        f"Got notifications: {notes!r}"
    )


async def test_create_entry_announces_the_resource_list_changed():
    notes: list[str] = []

    async def message_handler(message):
        if isinstance(message, ServerNotification):
            notes.append(type(message.root).__name__)

    async with connect(mcp, message_handler=message_handler) as client:
        await client.call_tool(
            "create_entry", {"title": "New leaf", "content": "Starting fresh."}
        )
        await anyio.sleep(0.1)

    assert "ResourceListChangedNotification" in notes, (
        "🚨 creating an entry changes the epicme://entries collection, so the "
        "server should send a ResourceListChangedNotification. "
        f"Got notifications: {notes!r}"
    )
