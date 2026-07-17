# MCP-UI — in Python

> Build on [**mcp-fundamentals**](../mcp-fundamentals). You already have a
> journal an AI app can read, write, and reason about. Here you give it a
> **face** — a server that sends UI, not just text.

Learn the **MCP-UI sub-spec**: an MCP server that returns *something to look at*
alongside a tool's answer, so a UI-aware client renders a tag card, a journal
page, or a full entry instead of a paragraph of prose.

The mechanism is small. A tool already returns content blocks. MCP-UI adds one
more kind: a **UI resource** — a block that says "render this" instead of "here
is some text." The whole spec is that one idea plus a `postMessage` conversation
once the UI is on screen.

This course reuses the EpicMe journal from mcp-fundamentals and adds three
`view_*` tools. It does **not** require [mcp-auth](../mcp-auth) — there are no
users or OAuth here, just the same single-user journal, now with a screen.

## Setup

You need [`uv`](https://docs.astral.sh/uv/getting-started/installation/). It
handles Python itself, so that's the only prerequisite.

```sh
uv sync
```

That's it. **No Node, no npm, no TypeScript** — not even for the demo. The
browser half ships as plain files `uv` already knows how to serve.

## The one idea

A UI resource is your server saying "render this," and the **mimeType** is how
the client knows what "this" is. The same block shape carries three things:

| content type | mimeType | `text` holds |
|---|---|---|
| rawHtml     | `text/html` | an HTML string the client drops into a frame |
| remoteDom   | `application/vnd.mcp-ui.remote-dom+javascript; framework=react` | a script that builds a DOM in the client's *own* design system |
| externalUrl | `text/uri-list` | a URL your server hosts, loaded in an iframe |

You never hand-assemble the block. `ui.py` gives you `create_ui_resource(...)`
(about 40 lines, hand-written — there's no Python `@mcp-ui/server` to install),
and your tool returns what it builds. UI resources use the `ui://` scheme
(`ui://view-tag/1`): unlike an `epicme://` URI, a `ui://` URI names *this
rendering*, not something the client can go fetch.

## How to work through it

Each exercise is a **problem** directory and a **solution** directory. You work
in the problem: open its `README.md`, read the lesson, then follow the `TODO`s
in `server.py` until the tests pass.

```sh
uv run pytest exercises/01.simple/01.problem.raw-html
```

The tests are in-memory wire-format checks — no browser, no ports. They assert
on the exact content block your tool returns. Run **one directory at a time**
(each exercise has its own `server.py`, so pytest can't collect them all).
Stuck? Diff your `server.py` against the `*.solution.*` dir next door.

One thing that trips people up: an unfinished tool `raise`s a
`NotImplementedError` placeholder, and FastMCP turns a raised error into an
error *result*. So the first failure you see is often an assertion like
`assert 'text' == 'resource'` — the content came back as an error text block,
not the resource you haven't built yet. That mismatch is expected until you
build and return the UI resource.

## The exercises

| # | Topic | What you build |
|---|-------|----------------|
| 01 | [simple](exercises/01.simple) | `view_tag(id)` returns a **rawHtml** card — an HTML string tagged `text/html` |
| 02 | [consistent](exercises/02.consistent) | `view_tag(id)` switches to a **remoteDom** script, so the card renders in the client's own design system |
| 03 | [complex](exercises/03.complex) | `view_journal()` returns an **externalUrl** into an iframe, then adds `preferred-frame-size` so the host sizes it before load |
| 04 | [interactive](exercises/04.interactive) | **Read-only.** The iframe measuring itself and posting tool/link/prompt messages back to the host — browser-only, so it lives in the demo, not a graded step |
| 05 | [advanced](exercises/05.advanced) | `view_entry(id)` returns a generic externalUrl carrying the entry as `initial-render-data` — the data travels in `_meta`, not the URL |

Topics 01, 02, 03, and 05 have graded steps. **Topic 04 has none, on purpose.**
The interactive half of MCP-UI — an iframe reporting its own height, a click
inside the frame posting a tool call back up to the host — is JavaScript running
in a browser by definition. You can't make an iframe run Python. So instead of a
graded step that would have to be browser JS, topic 04 is a walkthrough of those
concepts against the demo, where you watch them happen for real.

`preferred-frame-size` and `initial-render-data` (topics 03 and 05) are optional
`ui_metadata` that serialize into the resource's `_meta` under keys namespaced
`mcpui.dev/ui-<key>` — a `[width, height]` hint and a data payload handed to the
frame before its first paint.

## See it render

The tests prove your server emits the right resource *on the wire*. The **demo**
is the other half: a real browser rendering those resources, so you can watch a
tag card appear, a journal page load in an iframe, and a "View entry" click
travel back to the server as a tool call.

```sh
uv run python demo/app.py     # then open http://localhost:8788
```

Click the `view_*` buttons on the left. Each one calls the finished tool and
renders whatever UI resource it returns on the right, exactly the way a UI-aware
client would. Watch the **message log**: the `ui://` resource and its mimeType
coming back, the iframe's `ui-lifecycle-iframe-ready` handshake, `ui-size-change`
when the frame reports its height, and the `tool` / `link` / `prompt`
round-trips when you interact inside the frame.

The demo is not a hidden black box — it's fully-readable infrastructure you run,
read, and may edit. It covers the browser half that can't be Python. See
[`demo/README.md`](demo/README.md).

## What's Python and what isn't

The **graded path is pure Python**: your `server.py` builds UI resources, and
in-memory tests check the wire format. No browser is ever involved in a passing
test.

The **browser half is provided as vanilla JS** in `demo/` — a host renderer and
two iframe pages. Not because JavaScript is better here, but because iframes run
in a browser: the renderer branching on mimeType, a frame measuring itself, and
the `postMessage` conversation are things no server language can do. You run and
read that code; you don't grade it.

## Credit and license

This is a Python port of
[**mcp-ui**](https://github.com/epicweb-dev/mcp-ui) by
[EpicWeb.dev](https://www.epicweb.dev) (Kent C. Dodds), which teaches the same
sub-spec in TypeScript. The exercise idea and the EpicMe journal come from that
workshop; the Python code and all lesson text here were written fresh for this
port. Where upstream builds the interactive iframe steps in React, this port
keeps the graded work in Python and ships the browser half as a readable demo.

If TypeScript is your language, go do the original — it's excellent, and it comes
with a proper workshop app.

Licensed **GPL-3.0**, matching upstream. Upstream asks you to contact
team@epicweb.dev before running workshops with the material — worth honoring if
you ever teach this to a group rather than working through it yourself.
