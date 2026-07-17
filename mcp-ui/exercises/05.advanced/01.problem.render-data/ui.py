"""MCP-UI resources — infrastructure, not the lesson.

This is the one helper the UI course leans on: `create_ui_resource`. It turns a
description of some UI ("here's raw HTML", "here's a script that builds a DOM",
"here's a URL to put in an iframe") into an `EmbeddedResource` — the content
block your tool returns so a UI-aware client knows to *render* it instead of
printing text.

Upstream (the TypeScript workshop) imports this from a package called
`@mcp-ui/server`. There's no such package for Python, and it turns out there
doesn't need to be: the whole thing is about forty lines of assembling a
dictionary in the shape the MCP-UI spec describes. So it's written out here, in
the open, rather than hidden behind an install. Skim it once — the shapes it
produces are exactly what your tests assert — then treat it like `db.py`: given,
not edited.

The four moving parts of a UI resource:

  uri          A `ui://...` address. Unlike `epicme://...` resources, this URI
               is a name for *this rendering*, not something the client can go
               fetch. Two calls can share a URI (a stable widget) or vary it
               (`ui://view-journal/<timestamp>`) to force a fresh render.

  mimeType     How the client should interpret `text`. This is the load-bearing
               field — it's the difference between "parse this as HTML" and
               "treat this as a URL to load in an iframe".

  text         The payload itself: an HTML string, a DOM-building script, or a
               URL — whichever the mimeType promised.

  _meta        Out-of-band hints for the host frame (preferred size, initial
               data). Keys are namespaced `mcpui.dev/ui-...` so they never
               collide with anyone else's metadata.
"""

from __future__ import annotations

from typing import Any

from mcp.types import EmbeddedResource, TextResourceContents

# The three content shapes and the mimeType each one serializes to. The
# remote-dom type carries its framework in the mimeType parameter, the way a
# `Content-Type: text/html; charset=utf-8` header does.
_REMOTE_DOM_MIME = "application/vnd.mcp-ui.remote-dom+javascript; framework={framework}"


def create_ui_resource(
    uri: str,
    content: dict[str, Any],
    ui_metadata: dict[str, Any] | None = None,
) -> EmbeddedResource:
    """Build a UI resource content block.

    `content` is one of:

        {"type": "rawHtml",     "htmlString": "<div>...</div>"}
        {"type": "remoteDom",   "script": "root.appendChild(...)", "framework": "react"}
        {"type": "externalUrl", "iframeUrl": "https://.../ui/journal-viewer"}

    `ui_metadata` is an optional plain dict of hints for the host frame, e.g.
    `{"preferred-frame-size": ["600px", "800px"]}`. Each key is namespaced to
    `mcpui.dev/ui-<key>` on the way out.
    """
    kind = content["type"]
    if kind == "rawHtml":
        mime_type = "text/html"
        text = content["htmlString"]
    elif kind == "remoteDom":
        framework = content.get("framework", "react")
        mime_type = _REMOTE_DOM_MIME.format(framework=framework)
        text = content["script"]
    elif kind == "externalUrl":
        mime_type = "text/uri-list"
        text = content["iframeUrl"]
    else:
        raise ValueError(f"Unknown UI content type: {kind!r}")

    meta = None
    if ui_metadata:
        meta = {f"mcpui.dev/ui-{key}": value for key, value in ui_metadata.items()}

    resource = TextResourceContents(
        uri=uri,
        mimeType=mime_type,
        text=text,
        _meta=meta,
    )
    return EmbeddedResource(type="resource", resource=resource)
