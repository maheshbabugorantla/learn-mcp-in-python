"""Wire-format tests — frame sizing.

These run entirely in memory: no server process, no browser, no ports. Each test
calls a tool and asserts the *content block* it returns — the exact shape a
UI-aware client receives on the wire.
"""

from mcp.shared.memory import (
    create_connected_server_and_client_session as connect,
)

import server as server_module
from server import mcp


async def _call(name, args=None):
    async with connect(mcp) as client:
        return await client.call_tool(name, args or {})


def _block(result, i=0):
    return result.content[i].model_dump(by_alias=True, exclude_none=True, mode="json")


async def test_view_journal_has_preferred_frame_size():
    block = _block(await _call("view_journal"))
    resource = block["resource"]
    assert resource["mimeType"] == "text/uri-list"
    meta = resource.get("_meta")
    assert meta is not None, (
        "🚨 no _meta on the resource. Pass ui_metadata to create_ui_resource "
        "with a 'preferred-frame-size'."
    )
    assert meta == {"mcpui.dev/ui-preferred-frame-size": ["600px", "800px"]}, (
        "🚨 _meta should carry the preferred frame size. Got: %r" % meta
    )
