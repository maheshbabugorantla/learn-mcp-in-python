# Point an iframe at a page

`view_tag` inlined its UI — the whole card came back inside the resource. The
journal is bigger than a card: it's a page. So `view_journal()` won't ship the
page, it'll ship a **URL**, and the client will load that URL in an iframe.

## The externalUrl content type

`create_ui_resource` already knows this shape. You describe the content as an
`externalUrl` and give it the URL:

```py
content={"type": "externalUrl", "iframeUrl": iframe_url}
```

`iframeUrl` is the input key. On the wire, that becomes a resource with mimeType
`text/uri-list` and its `text` set to the URL — a single line, the one address
the iframe should load. That's the whole payload: no HTML, no script, just where
to go.

## Where the page lives

`BASE_URL` at the top of `server.py` is where the demo serves the journal page:

```py
BASE_URL = os.environ.get("EPICME_BASE_URL", "http://localhost:8788")
```

The demo app (`mcp-ui/demo/app.py`) hosts the page at `/ui/journal-viewer`, so
the URL you build is `f"{BASE_URL}/ui/journal-viewer"`. Your server isn't
rendering the journal — it's telling the client where the server *hosts* it.

## A fresh URI every call

Give the resource a `ui://` URI, and make it a fresh one each time:

```py
uri=f"ui://view-journal/{int(time.time() * 1000)}"
```

A `ui://` URI names *this rendering*, not something fetchable. The millisecond
timestamp makes every call a distinct id, so the host treats each one as a new
frame to load rather than reusing a stale one.

## Your task

Open `server.py` and follow the TODOs in `view_journal()`: build the iframe URL,
then return a `CallToolResult` whose one content block is the `externalUrl` UI
resource. Delete the `NotImplementedError` placeholder when you do.

```sh
uv run pytest exercises/03.complex/01.problem.iframe
```

Before you write anything, the first failure is worth reading. The unfinished
tool `raise`s `NotImplementedError`, and FastMCP wraps a raised error into an
error *result* — a plain text block. So the test fails at
`assert block["type"] == "resource"` with the block coming back as `"text"`
instead. That mismatch is exactly what an unbuilt UI resource looks like; it
clears the moment you return the real one.

Stuck? Diff against `../01.solution.iframe/`.

## What's next?

Next you will tell the host how big to make the frame *before* the page loads.
Right now the client has a URL and no idea what shape the thing at the other end
is, so it has to guess and then correct itself once the page can measure.
