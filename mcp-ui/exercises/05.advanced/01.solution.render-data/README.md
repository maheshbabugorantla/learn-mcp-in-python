# Render data

`view_entry` now hands the entry to the page instead of making the page go get
it:

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

On the wire that's a `text/uri-list` resource whose `text` is a **generic** URL —
no id — and whose `_meta` carries the entry under
`mcpui.dev/ui-initial-render-data`. The insight is the direction of flow: instead
of the page *pulling* its data with a second request, the server *pushes* the
data up front, so the page can paint immediately from what it was handed.

See it in the demo. Run `uv run python demo/app.py`, open
<http://localhost:8788>, and click **view_entry**. The entry-viewer page renders
the entry — title, mood, body — with no fetch of its own; it got everything from
the render data the host passed in. That's `waitForRenderData()` on the receiving
end of the `_meta` you just produced.
