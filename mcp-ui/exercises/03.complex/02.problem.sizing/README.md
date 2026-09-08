# Size the frame before it loads

`view_journal()` returns the right URL now, but the host has a chicken-and-egg
problem: it has to create the iframe *before* the page inside it has loaded and
measured itself. Until the page posts its first `ui-size-change`, the host is
guessing at how big the frame should be.

You can give it a better guess. A UI resource can carry out-of-band hints for the
host in its metadata, and one of them is exactly this:

```py
ui_metadata={"preferred-frame-size": ["600px", "800px"]}
```

That's a `[width, height]` pair. Pass it to `create_ui_resource`, and it
serializes into the resource's `_meta` under a namespaced key:

```json
"_meta": { "mcpui.dev/ui-preferred-frame-size": ["600px", "800px"] }
```

The `mcpui.dev/ui-` prefix keeps MCP-UI's hints from colliding with anyone
else's metadata.

## Why a static hint, when the page sizes itself anyway

Because the timing is different, and both matter. Look at what the demo host does
in `demo/pages.py`:

- **Before load** — when it builds the iframe, it reads
  `mcpui.dev/ui-preferred-frame-size` and applies it immediately: width to the
  wrapper's `max-width`, height to the frame, overriding its default. The frame
  is the right size on the very first paint, before the page has said a word.
- **After load** — once the page is running, its `ResizeObserver` posts
  `ui-size-change`, and the host's handler overrides the height from the *real*
  measured content.

So the static hint gets the frame close instantly and stops the layout from
jumping; the dynamic sizing corrects it to the truth once the browser can
measure. The hint is Python you write here. The dynamic half is in-browser
JavaScript — read it in the demo.

## Your task

Open `server.py` and follow the TODO in `view_journal()`: add the `ui_metadata`
with a `preferred-frame-size` of `["600px", "800px"]`. The externalUrl resource
from the last step stays exactly as it is.

```sh
uv run pytest exercises/03.complex/02.problem.sizing
```

Stuck? Diff against `../02.solution.sizing/`.

## What's next?

That hint is the host's opening line in a conversation you haven't watched yet.
**Interactive UI** has nothing to run — the rest is browser JavaScript — so it is
a read-through of the demo, where the page reports its real size, asks the host
to call tools, and gets answers back.
