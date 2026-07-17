"""Wire-format tests — remote DOM.

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


REMOTE_MIME = "application/vnd.mcp-ui.remote-dom+javascript; framework=react"


async def test_view_tag_returns_remote_dom_for_known_tag():
    block = _block(await _call("view_tag", {"id": 1}))
    assert block["type"] == "resource"
    resource = block["resource"]
    assert resource["uri"] == "ui://view-tag/1"
    assert resource["mimeType"] == REMOTE_MIME, (
        "🚨 a remote-dom resource has mimeType %r. Got: %r"
        % (REMOTE_MIME, resource.get("mimeType"))
    )
    text = resource["text"]
    for needle in ("document.createElement", "root.appendChild", "ui-stack", "home"):
        assert needle in text, (
            "🚨 the remote-dom script should contain %r. Got: %r" % (needle, text)
        )


async def test_view_tag_remote_dom_not_found():
    block = _block(await _call("view_tag", {"id": 999}))
    resource = block["resource"]
    assert resource["mimeType"] == REMOTE_MIME
    assert "not found" in resource["text"].lower()
    assert "document.createElement" in resource["text"]
