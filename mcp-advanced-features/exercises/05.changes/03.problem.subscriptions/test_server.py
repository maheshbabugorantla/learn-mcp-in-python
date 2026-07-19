"""Resource subscription tests — watching one specific entry.

The client subscribes to a single resource URI, then we edit it and check that a
`ResourceUpdatedNotification` for that URI arrives via the `message_handler`. A
second test edits an entry nobody subscribed to and confirms the server stays
quiet — the point of subscriptions is that you only hear about what you asked
for.
"""

import anyio
from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import ServerNotification
from pydantic import AnyUrl

from server import db, mcp


async def test_updating_a_subscribed_entry_notifies():
    if db.get_entry(1) is None:
        db.seed()
    notes: list[str] = []

    async def message_handler(message):
        if isinstance(message, ServerNotification):
            notes.append(type(message.root).__name__)

    async with connect(mcp, message_handler=message_handler) as client:
        await client.subscribe_resource(AnyUrl("epicme://entries/1"))
        await client.call_tool("update_entry", {"id": 1, "mood": "wistful"})
        await anyio.sleep(0.1)

    assert "ResourceUpdatedNotification" in notes, (
        "🚨 updating a subscribed entry should send a ResourceUpdatedNotification "
        f"for epicme://entries/1. Got notifications: {notes!r}"
    )


async def test_updating_an_unsubscribed_entry_stays_quiet():
    if db.get_entry(2) is None:
        db.seed()
    notes: list[str] = []

    async def message_handler(message):
        if isinstance(message, ServerNotification):
            notes.append(type(message.root).__name__)

    async with connect(mcp, message_handler=message_handler) as client:
        # Subscribe to entry 1, but change entry 2. No one is watching 2.
        await client.subscribe_resource(AnyUrl("epicme://entries/1"))
        await client.call_tool("update_entry", {"id": 2, "mood": "restless"})
        await anyio.sleep(0.1)

    assert "ResourceUpdatedNotification" not in notes, (
        "🚨 only subscribed resources should notify — updating the unsubscribed "
        f"entry 2 should send no ResourceUpdatedNotification. Got: {notes!r}"
    )
