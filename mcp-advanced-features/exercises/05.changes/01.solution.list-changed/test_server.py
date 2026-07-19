"""tools/list_changed tests — watching the server announce a new tool.

The client passes a `message_handler`: a callback that sees every message the
server pushes, including notifications. We collect the class names of the
`ServerNotification`s that arrive, call `enable_beta_tools`, and check that a
`ToolListChangedNotification` showed up — and that the newly-registered
`beta_ping` really is in the tool list afterward.
"""

import anyio
from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import ServerNotification

from server import mcp


async def test_enable_beta_tools_announces_the_change():
    notes: list[str] = []

    async def message_handler(message):
        if isinstance(message, ServerNotification):
            notes.append(type(message.root).__name__)

    async with connect(mcp, message_handler=message_handler) as client:
        await client.call_tool("enable_beta_tools", {})
        # Notifications are fire-and-forget; give the client a beat to receive it.
        await anyio.sleep(0.1)
        tools = await client.list_tools()
        names = {t.name for t in tools.tools}

    assert "ToolListChangedNotification" in notes, (
        "🚨 enabling beta tools should send a ToolListChangedNotification so the "
        f"client knows to re-fetch. Got notifications: {notes!r}"
    )
    assert "beta_ping" in names, (
        "🚨 after enabling beta tools, `beta_ping` should appear in the tool list. "
        f"Got: {sorted(names)!r}"
    )
