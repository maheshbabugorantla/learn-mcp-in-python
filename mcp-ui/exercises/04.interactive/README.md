# Interactive UI

Everything so far has been one-directional: your server emits a UI resource, the
client renders it, done. But a rendered page is not a picture — it has buttons.
When someone clicks one, the page inside the iframe needs to make something
happen back on the outside: open a link, call another tool, run a prompt. This
topic is about that conversation.

## Why there's no exercise to run here

The other topics each have a `server.py` with a 🐨 TODO. This one doesn't, and
that's deliberate — not a gap.

Interactivity is the iframe talking to its host, and an iframe runs **browser
JavaScript**, not Python. There's no server code to write here because the whole
mechanism — the clicking, the message passing, the acting on those messages —
lives in the browser, after your resource is already on screen. The tools an
interaction ends up calling are ordinary MCP tools you're building elsewhere in
this course (`view_journal`, which you already built; `view_entry`, which you'll
build next in topic 05). There's nothing new to write on the server for the
*interaction* itself.

Upstream (the TypeScript workshop this course is based on) writes this half in
React, and roughly seven of its steps live entirely in that in-browser layer. We
can't translate those to Python and pretend an iframe runs it. So instead of a
fake exercise, this topic is a guided read of a **real, running demo** under
`mcp-ui/demo/` — vanilla JS, nothing hidden — where you watch the whole
round-trip happen for real.

## Run the demo

```sh
uv run python demo/app.py
```

Then open <http://localhost:8788>. Click **view_journal** on the left. The host
calls your `view_journal` tool, gets back an `externalUrl` resource, and loads
`/ui/journal-viewer` into an iframe. You'll see your entries listed, each with a
**View entry** button.

Now click one of those **View entry** buttons and watch the **Message log** on
the left. You'll see a `tool` line go up (`→`) and a `ui-message-response` line
come back (`←`). That is the entire interaction protocol, live.

## What just happened, function by function

The plumbing lives in `demo/pages.py`. Three functions carry the conversation:

- **`sendMcpMessage(type, payload)`** (iframe side). The journal page's button
  calls `sendMcpMessage('tool', {toolName: 'view_entry', params: {id}})`. The
  iframe can't reach your server — it's sandboxed — so it does the only thing it
  can: `window.parent.postMessage(...)`, handing the request *up* to whoever is
  hosting it. Each message gets a unique `messageId`, and the function returns a
  Promise that resolves when a reply with that same id comes back.

- **The host's `message` handler** (host side, in `HOST_PAGE`). It listens for
  messages posted up from the iframe. When it sees an action message, it *acts*
  (the three verbs are below), then posts a **`ui-message-response`** back down,
  keyed to the original `messageId`, so the waiting Promise on the iframe side
  can resolve.

- **`waitForRenderData()`** (iframe side). A second, simpler flavor of the same
  idea, used by the entry-viewer page — you'll meet it properly in topic 05. The
  page announces it's ready and then waits for the host to hand it data, rather
  than posting a request and awaiting a reply.

The shape is always the same: **the iframe posts a message up, the host does the
thing only it can do, and the host posts a response back down.** The three action
verbs are just three flavors of that one grammar:

- **`tool`** — "call this tool for me." The host runs it and hands the result
  back. This is the one you just watched: a journal button asks for `view_entry`.
- **`link`** — "open this URL." The iframe can't navigate the outer page, so it
  asks the host to open the link.
- **`prompt`** — "run this prompt." The iframe hands a prompt string up and the
  host (a real client) feeds it to the model.

Read `demo/pages.py` end to end at least once — every `view_*` resource you build
in Python is driving something in that file, and this is where you watch it move.
