"""EpicMe UI demo — the renderer you read and run, not the lesson.

The exercises prove, in memory, that your server emits the right UI resource on
the wire. This app is the other half: a real browser rendering those resources,
so you can *see* a tag card appear, a journal page load in an iframe, and a
"View entry" click travel back to the server as a tool call.

It is deliberately not an MCP client. The exercises and mcp-fundamentals already
cover MCP transport; re-implementing it in browser JavaScript would only get in
the way of the thing this demo is about — the UI. So the browser talks to a
plain endpoint here, `/demo/call/<tool>`, which runs the real tool in-process
and hands back the exact content block a UI-aware MCP client would receive. From
there on, everything — the mimeType switch, the iframe, the postMessage
handshake, the sizing, the tool round-trip — is the genuine MCP-UI machinery.

Run it:

    uv run python demo/app.py        # then open http://localhost:8788

Everything it serves is in this folder and fully commented:

    app.py       this file: the routes and the in-process tool bridge
    pages.py     the HTML/JS for the host page and the two iframe pages
    server.py    the finished EpicMe MCP server (same one you build)
    ui.py, db.py the provided infrastructure
"""

from __future__ import annotations

import json
import os

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse
from starlette.routing import Route
from mcp.shared.memory import (
    create_connected_server_and_client_session as connect,
)

import pages
from server import db, mcp

PORT = int(os.environ.get("EPICME_PORT", "8788"))


async def host_page(request: Request) -> HTMLResponse:
    """The renderer: pick a tool, call it, render whatever UI it returns."""
    return HTMLResponse(pages.HOST_PAGE)


async def journal_viewer(request: Request) -> HTMLResponse:
    """The iframe page `view_journal` points at. Lists entries; talks to its host."""
    entries = [
        {"id": e.id, "title": e.title, "content": e.content} for e in db.get_entries()
    ]
    html = pages.JOURNAL_VIEWER.replace("__ENTRIES__", json.dumps(entries))
    return HTMLResponse(html)


async def entry_viewer(request: Request) -> HTMLResponse:
    """The iframe page `view_entry` points at. Waits for its data from the host."""
    return HTMLResponse(pages.ENTRY_VIEWER)


async def call_tool(request: Request) -> JSONResponse:
    """Run a tool over an in-memory MCP session and return its content as JSON.

    This is the stand-in for an MCP client's tool call. It uses the very same
    in-memory session the exercise tests use — a real client session wired to
    this server in-process — so the browser gets back exactly the content blocks
    your tests assert on, through the public API, not a private back door.
    """
    tool_name = request.path_params["tool"]
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    async with connect(mcp) as session:
        result = await session.call_tool(tool_name, payload)

    blocks = [
        block.model_dump(by_alias=True, exclude_none=True, mode="json")
        for block in result.content
    ]
    return JSONResponse({"content": blocks, "isError": bool(result.isError)})


async def healthcheck(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


app = Starlette(
    routes=[
        Route("/", host_page),
        Route("/ui/journal-viewer", journal_viewer),
        Route("/ui/entry-viewer", entry_viewer),
        Route("/demo/call/{tool}", call_tool, methods=["POST"]),
        Route("/healthcheck", healthcheck),
    ]
)


if __name__ == "__main__":
    print(f"EpicMe UI demo on http://localhost:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
