# You're done

You started with tools that answered in text — a sentence, a JSON blob, a link —
which is exactly right when a language model is the only reader. You now have a
server that, when a *person* is looking, hands the client something to render.
Same journal, same tools; a second channel added alongside the words.

Here's what you built, five ways of saying "render this":

- **Raw HTML.** The blunt one. You write the markup, tag it `text/html`, the
  client draws it as-is. Simple, and it looks like *your* card wherever it lands.
- **Remote DOM.** A script that builds the card out of the client's own elements
  (`ui-stack`, `ui-text`) instead of your markup — so it comes out looking native
  to whatever app rendered it. The mimeType even carries the framework, the way
  `Content-Type` carries a charset.
- **An external URL in an iframe.** `view_journal` returns a `text/uri-list`
  pointing at a page your server hosts — a whole HTML document, not a snippet,
  loaded into a frame.
- **A frame-size hint.** `preferred-frame-size` in `_meta`, telling the host how
  big to make the frame *before* the page has said anything.
- **Initial render data.** `view_entry` hands the entry up front in `_meta`, so
  the page paints from data it was given instead of fetching it — and the URL
  goes generic, because the state moved out of the address and into the metadata.

## The one idea underneath all five

A UI resource is your server saying **"render this,"** and the **mimeType** is how
the client knows what "this" is. `text/html`, `text/uri-list`, the
`remote-dom+javascript` type — that single field is the whole switch. Everything
else is `_meta`: out-of-band hints that don't change *what* to render, only how to
fit it and what to feed it.

And once it's on screen, the second half kicks in: **a postMessage conversation.**
The iframe posts a message up (`tool`, `link`, `prompt`, or a request for its
render data), the host does the thing only it can do, and the host posts a
response back down. You watched every piece of that run in the demo. The whole
MCP-UI spec is those two things — a resource that says "render this," and a small
message protocol for what happens after.

## The part where you find out about the real library

Now that you know what the machinery is, here's the shortcut.

Upstream — the TypeScript workshop this course is based on — imports two packages:
`@mcp-ui/server` builds these resources, and `@mcp-ui/client` renders them in the
browser. Our `create_ui_resource` in `ui.py` is the server half, written out in
about forty lines, because there's no Python package for it and it turns out
there doesn't need to be: it's just assembling a content block in the shape the
spec describes. Read it again now and you'll recognize every branch — `rawHtml` →
`text/html`, `externalUrl` → `text/uri-list`, the `mcpui.dev/ui-` namespacing on
`_meta`. That's the difference between calling a library and being able to debug
one: when a client renders your resource wrong, you'll know whether the bug is in
the mimeType, the payload, or the metadata key.

## Where to go next

**Run the demo again, slowly.** Two things worth doing by hand:

```sh
uv run python demo/app.py        # then open http://localhost:8788
```

Click each tool and watch the message log. Then open `demo/pages.py` and read it
top to bottom — the host's mimeType switch, `sendMcpMessage`, the host message
handler, `waitForRenderData`. Every Python resource you built is driving a few
lines in there. Seeing them connected is the point.

**Read the spec.** The [MCP-UI spec](https://mcpui.dev) is short and will now read
like a description of something you've already met — the `ui://` scheme, the
content types, the `mcpui.dev/ui-*` metadata keys, the lifecycle messages.

**Then be honest about what this course left out.** The browser half — the host
renderer and the two iframe pages — is *provided*, not something you hand-wrote,
because an iframe runs JavaScript and no amount of Python changes that. Our demo
is also a faithful stand-in, not a shipping client: it maps remote-dom onto plain
divs and calls tools over a plain endpoint instead of full MCP transport. Real
UI-aware clients — Goose, Postman's MCP support, and others — render these
resources for real, in their own design systems, over a real connection. The half
you learned is the half you actually write: the server deciding what to show and
handing it over in the right shape.

Nice work. Go build something worth looking at.
