# Size the frame before it loads

One argument on the resource, and the host now knows how big to make the frame
from the start:

```py
create_ui_resource(
    uri=f"ui://view-journal/{int(time.time() * 1000)}",
    content={"type": "externalUrl", "iframeUrl": iframe_url},
    ui_metadata={"preferred-frame-size": ["600px", "800px"]},
)
```

That serializes to `_meta["mcpui.dev/ui-preferred-frame-size"]`, and it's a
*hint*, not a command — the host is free to use it or ignore it.

The pairing is the thing to remember. Frame sizing happens twice, from two
sides:

- **Static, before load** — this hint, sent by your server, so the host can size
  the frame on first paint with nothing to jump.
- **Dynamic, after load** — the page's own `ResizeObserver` posting
  `ui-size-change`, so the frame tracks the real content as it changes.

The first is Python you just wrote; the second is browser JavaScript you don't.
Run the demo and click `view_journal` to watch both: the frame comes up at the
hinted size, then settles to what the page actually measures.

```sh
uv run python demo/app.py        # then open http://localhost:8788
```
