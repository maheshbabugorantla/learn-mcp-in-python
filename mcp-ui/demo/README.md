# The EpicMe UI demo

The exercises prove, in memory, that your server emits the right UI resource on
the wire. This demo is the other half: a **real browser rendering those
resources**. It's the renderer and the two iframe pages that make the browser
side of MCP-UI real — the part no server language can reach.

## Run it

From the `mcp-ui` directory:

```sh
uv run python demo/app.py     # then open http://localhost:8788
```

## What the buttons do

Each button on the left calls a finished `view_*` tool and renders whatever UI
resource comes back, branching on its mimeType:

- **`view_tag {id: 1}`** — a remoteDom script; the renderer runs it against a
  tiny `ui-stack` / `ui-text` vocabulary and a tag card appears.
- **`view_tag {id: 999}`** — the same tool with a missing id, so you see the
  "not found" rendering.
- **`view_journal {}`** — an externalUrl; the renderer loads the hosted
  journal page into an iframe. Click **View entry** inside it and the frame
  posts a tool call *up* to the host, which runs `view_entry` for it.
- **`view_entry {id: 1}`** — an externalUrl with no id in the URL. The entry
  rides along as `initial-render-data` in `_meta`; the host hands it to the
  frame after the ready handshake, and the frame paints from it — no fetch.

## What the message log shows

The panel under the buttons traces the `postMessage` conversation:

- `resource ui://…  (mimeType)` — the block the tool returned.
- `ui-lifecycle-iframe-ready` — the frame announcing it's loaded.
- `preferred-frame-size` / `ui-size-change` — the host sizing the frame up
  front, then the frame reporting its own height as content changes.
- `tool` / `link` / `prompt` and `ui-message-response` — an action the frame
  asked the host to take, and the host's reply, matched by message id.

## What to read

Everything the demo serves is in this folder, vanilla and fully commented — no
framework, no build step:

- **`app.py`** — the routes and the in-process tool bridge.
- **`pages.py`** — the host renderer and the two iframe pages, as HTML/JS.
- **`server.py`** — the finished EpicMe server (the same one you build in the
  exercises); `ui.py` and `db.py` are the provided infrastructure.

Read it to see what your Python-emitted resources actually drive. Edit it if
you're curious — nothing here is hidden or minified.

## Not a real MCP client

This is a teaching stand-in, not an MCP client. When you click a button, the
page POSTs to `/demo/call/<tool>`, which runs the real tool over an **in-process
in-memory MCP session** — the same session the exercise tests use — and hands
back the exact content block a UI-aware client would receive. It is *not*
MCP-over-HTTP; re-implementing transport in browser JavaScript would only get in
the way of the thing this demo is about, the UI. From the resource onward —
the mimeType switch, the iframe, the sizing, the postMessage round-trips —
everything is the genuine MCP-UI machinery. A real UI-aware client renders these
same resources the same way.
