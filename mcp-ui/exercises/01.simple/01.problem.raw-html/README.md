# Raw HTML

The EpicMe journal from mcp-fundamentals is all here — entries, tags, resources.
That's background. Your work is one tool: `view_tag`. Right now it looks up a tag
and then gives up:

```py
@mcp.tool()
def view_tag(id: ...) -> CallToolResult:
    """View a tag visually — returns a UI resource, not plain text."""
    tag = db.get_tag(id)
    raise NotImplementedError("Build and return the UI resource (see the TODO).")
```

## Your job

Return a `CallToolResult` whose single content block is a UI resource built by
`create_ui_resource(...)`. There's a helper next to `view_tag` — `_tag_html(tag, id)` —
that already turns a tag into a small HTML card (or a "not found" message). You
supply the two arguments:

- `uri` — `f"ui://view-tag/{id}"`, the address that names this render
- `content` — `{"type": "rawHtml", "htmlString": _tag_html(tag, id)}`

Then delete the `raise` placeholder.

## The wire shape you're producing

`create_ui_resource` assembles the block; the tests assert its exact shape. A
`rawHtml` resource serializes to:

```
type:              "resource"
resource.uri:      "ui://view-tag/1"
resource.mimeType: "text/html"
resource.text:     "<div><h1>home</h1>...</div>"    ← the HTML string
```

The `rawHtml` content type maps to mimeType `text/html`, and the `htmlString` you
pass becomes `resource.text`. That's the whole translation.

## About the failure you'll see first

Run the tests before you build anything and the first failure looks strange —
something like `assert 'text' == 'resource'`. That's expected. The unfinished tool
`raise`s `NotImplementedError`, FastMCP catches that and returns it as an *error*
result — a `text` block carrying the message — so the test finds a `text` block
where it wanted your `resource`. It isn't a bug in the test; it's the placeholder
talking. Build and return the UI resource and the mismatch goes away.

```sh
uv run pytest exercises/01.simple/01.problem.raw-html
```

Stuck? Diff your `server.py` against the sibling
[`01.solution.raw-html`](../01.solution.raw-html/server.py).

## What's next?

Next, **Consistent UI** rewrites this same tool around a different content type.
The block shape and the `ui://` URI stay put; the mimeType changes, and so does
what rides in `resource.text`.
