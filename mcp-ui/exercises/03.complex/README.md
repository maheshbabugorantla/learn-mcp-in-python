# Complex UI

Raw HTML and remote-dom both inline the UI: the whole thing rides along in the
tool's response as a string the client renders. That works for a card. It stops
working when the UI is a whole page — its own stylesheet, its own scripts, state
that changes as you click around. You don't want to stuff a page into a string.

So you don't. You **host the page** — serve it at a URL the way you'd serve any
web page — and the UI resource just hands the client that URL. The client drops
it into an **iframe**. The content type is `externalUrl`, and its mimeType is
`text/uri-list`: not "here is the UI," but "here is where the UI lives, go load
it."

## What happens once the page is in the iframe

An iframe isn't a static picture. Once the client loads your page, the two sides
start talking over `postMessage`, and MCP-UI defines a small protocol for it:

- **The ready handshake.** The moment the page loads, it announces itself by
  posting `ui-lifecycle-iframe-ready` up to the host. That's the page saying
  "I'm here, you can talk to me now."
- **Size reporting.** The page measures itself and posts `ui-size-change` with
  its height, so the host can fit the frame to the content instead of guessing.
- **Dynamic sizing.** The page keeps a `ResizeObserver` on its own body. When
  the content grows or shrinks — an entry expands, an image loads — it re-posts
  `ui-size-change`, and the host resizes the frame to match.

## Why half of this topic is a demo, not an exercise

Read that list again: the handshake, the measuring, the `ResizeObserver`. Every
one of them runs *inside the iframe, in the browser*. It's JavaScript by
definition — you cannot make an iframe run Python, and there's no honest way to
"grade" a `postMessage` in an in-memory test.

So this course splits the work where the language boundary actually falls:

- The **browser half** ships as a runnable demo under `mcp-ui/demo/`. It's
  vanilla JavaScript, fully readable, nothing hidden. Run it and watch the
  handshake fire, the frame resize itself, the whole lifecycle happen for real:

  ```sh
  uv run python demo/app.py        # then open http://localhost:8788
  ```

  Click `view_journal`, open your browser's console, and read `demo/pages.py`
  alongside it — the ready message, the `ui-size-change` posts, and the host's
  handler that resizes the frame are all right there.

- The **server half** — the part that *is* Python — is what you build here, in
  two graded steps:

  1. **The externalUrl (`01.problem.iframe`).** Write `view_journal()` so it
     returns a UI resource pointing an iframe at the page your server hosts.
  2. **The static preferred frame size (`02.problem.sizing`).** Add a metadata
     hint so the host sizes the frame *before* the page even loads — the
     counterpart to the dynamic sizing the page does *after*, in the browser.

The recurring idea still holds: a UI resource is your server saying "render
this," and the mimeType is how the client knows what "this" is. Here "this" is a
URL, and everything after the load is the iframe conversation the demo shows you.

## What's next?

Both steps here hand the client an address and stop there. **Interactive UI**
picks up where that leaves off: once the page is loaded and on screen, it and the
host still have plenty to say to each other, and that traffic is the whole
subject of the next topic.
