"""Wire-format tests — raw HTML.

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


async def test_view_tag_returns_html_for_known_tag():
    block = _block(await _call("view_tag", {"id": 1}))
    assert block["type"] == "resource", (
        "🚨 view_tag should return a `resource` content block. Build it with "
        "create_ui_resource(...). Got: %r" % block.get("type")
    )
    resource = block["resource"]
    assert resource["uri"] == "ui://view-tag/1", (
        "🚨 the resource uri should be 'ui://view-tag/1'. Got: %r" % resource.get("uri")
    )
    assert resource["mimeType"] == "text/html", (
        "🚨 a rawHtml resource has mimeType 'text/html'. Got: %r"
        % resource.get("mimeType")
    )
    assert "home" in resource["text"], (
        "🚨 the HTML should contain the tag name ('home' for tag 1). Got: %r"
        % resource["text"]
    )


async def test_view_tag_returns_not_found_for_unknown_tag():
    block = _block(await _call("view_tag", {"id": 999}))
    resource = block["resource"]
    assert resource["uri"] == "ui://view-tag/999"
    assert resource["mimeType"] == "text/html"
    assert "not found" in resource["text"].lower(), (
        "🚨 an unknown tag should render a 'not found' message. Got: %r"
        % resource["text"]
    )
