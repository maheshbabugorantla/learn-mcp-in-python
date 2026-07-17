"""Wire-format tests — iframe.

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


async def test_view_journal_returns_external_url():
    block = _block(await _call("view_journal"))
    assert block["type"] == "resource"
    resource = block["resource"]
    assert resource["uri"].startswith("ui://view-journal/"), (
        "🚨 the uri should start with 'ui://view-journal/'. Got: %r"
        % resource.get("uri")
    )
    assert resource["mimeType"] == "text/uri-list", (
        "🚨 an externalUrl resource has mimeType 'text/uri-list'. Got: %r"
        % resource.get("mimeType")
    )
    assert resource["text"] == f"{server_module.BASE_URL}/ui/journal-viewer", (
        "🚨 the text should be the iframe URL. Got: %r" % resource.get("text")
    )


async def test_view_tag_still_remote_dom():
    # Earlier work keeps working.
    block = _block(await _call("view_tag", {"id": 1}))
    assert "framework=react" in block["resource"]["mimeType"]
