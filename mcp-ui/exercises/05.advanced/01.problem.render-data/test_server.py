"""Wire-format tests — render data.

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


async def test_view_entry_carries_initial_render_data():
    block = _block(await _call("view_entry", {"id": 1}))
    resource = block["resource"]
    assert resource["uri"] == "ui://view-entry/1"
    assert resource["mimeType"] == "text/uri-list"
    assert resource["text"] == f"{server_module.BASE_URL}/ui/entry-viewer", (
        "🚨 the URL should be generic (no id) — the entry travels in _meta. Got: %r"
        % resource.get("text")
    )
    meta = resource.get("_meta")
    assert meta is not None, "🚨 no _meta. Pass ui_metadata with 'initial-render-data'."
    data = meta.get("mcpui.dev/ui-initial-render-data")
    assert data is not None, (
        "🚨 _meta should have key 'mcpui.dev/ui-initial-render-data'. Got: %r" % meta
    )
    assert data["entry"]["id"] == 1
    assert data["entry"]["title"] == "A quiet morning"


async def test_view_entry_unknown_raises():
    result = await _call("view_entry", {"id": 999})
    assert result.isError, "🚨 an unknown entry id should be an error"
