# Point an iframe at a page

`view_journal()` now returns a UI resource that carries nothing but a URL:

```py
iframe_url = f"{BASE_URL}/ui/journal-viewer"
return CallToolResult(
    content=[
        create_ui_resource(
            uri=f"ui://view-journal/{int(time.time() * 1000)}",
            content={"type": "externalUrl", "iframeUrl": iframe_url},
        )
    ]
)
```

That's the shift worth holding onto. With raw HTML or remote-dom the server
*is* the UI — the markup or the script rides in the response. With `externalUrl`
the server only *points at* the UI: it hosts a page and hands the client a
`text/uri-list` resource saying "load this in an iframe." The page can be as big
and as stateful as any web page, because it isn't crammed into a string.

The fresh `ui://view-journal/<timestamp>` URI keeps each call distinct, so the
host loads a new frame rather than reusing an old rendering.

Want to see it actually load? Run the demo and click `view_journal`:

```sh
uv run python demo/app.py        # then open http://localhost:8788
```

The journal page appears in a real iframe — and the moment it loads, the
lifecycle from the topic intro kicks in: the ready handshake, the size report.
That half is browser JavaScript, waiting in `demo/pages.py` for you to read.
