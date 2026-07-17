# Render data

There's a new tool this time: `view_entry(id)`. It looks the entry up, confirms
it exists, and then gives up:

```py
@mcp.tool()
def view_entry(id: ...) -> CallToolResult:
    entry = db.get_entry(id)
    if entry is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    raise NotImplementedError("Return the UI resource with render data (see the TODO).")
```

Like `view_journal`, it returns an `externalUrl` resource — a page loaded into an
iframe. The difference is where the entry's data comes from.

## Your job

Return a `CallToolResult` whose single content block is a UI resource:

- **A generic iframe URL** — `f"{BASE_URL}/ui/entry-viewer"`, with **no id in
  it**.
- **The entry carried as metadata** — pass
  `ui_metadata={"initial-render-data": {"entry": entry.to_dict()}}`.

```py
iframe_url = f"{BASE_URL}/ui/entry-viewer"
return CallToolResult(
    content=[
        create_ui_resource(
            uri=f"ui://view-entry/{id}",
            content={"type": "externalUrl", "iframeUrl": iframe_url},
            ui_metadata={"initial-render-data": {"entry": entry.to_dict()}},
        )
    ]
)
```

Then delete the `raise` placeholder.

## Why the id leaves the URL

It's tempting to write `/ui/entry-viewer/{id}` and let the page fetch the entry
itself. Don't. You already have the entry — `db.get_entry(id)` returned it two
lines up. Putting it in `ui_metadata` hands it to the page directly, so the page
never has to fetch anything, and the URL never has to name anything. One generic
page renders every entry, because the data rides along in `_meta` instead of in
the address.

## The wire shape you're producing

`create_ui_resource` puts your `ui_metadata` into the resource's `_meta`,
namespacing each key with `mcpui.dev/ui-`. So `initial-render-data` becomes:

```
resource.uri:      "ui://view-entry/1"
resource.mimeType: "text/uri-list"
resource.text:     "http://localhost:8788/ui/entry-viewer"   ← generic, no id
resource._meta:    {"mcpui.dev/ui-initial-render-data": {"entry": {...}}}
```

That `_meta` key is exactly what the demo's host reads and posts down to the
entry-viewer frame.

## About the failure you'll see first

Run the tests before you build anything and the first failure looks off —
something like `assert 'text' == 'resource'`. That's the placeholder talking. The
unfinished tool `raise`s `NotImplementedError`; FastMCP turns that into an
*error* result — a `text` block — so the test finds a `text` block where it
wanted your `resource`. Build and return the UI resource and the mismatch clears.

```sh
uv run pytest exercises/05.advanced/01.problem.render-data
```

Stuck? Diff your `server.py` against the sibling
[`01.solution.render-data`](../01.solution.render-data/server.py).
