# Changes

Every feature so far in this course has been the server speaking up mid-call: it
asked the user something (elicitation), asked the model something (sampling),
reported as it worked (progress), and accepted a stop (cancellation). This topic
is the last variety of the same idea, and the most matter-of-fact: the server
telling the client **"something you're holding is now stale — look again."**

Basic MCP is request/response, and a client that has fetched your tool list or a
resource collection caches it. That's fine until the truth moves out from under
it. A tool appears at runtime; a new entry lands in the journal; a resource the
client is watching gets edited. The client has no way to know unless you tell it.
These notifications are how you tell it.

## Two grains of "something changed"

There are two, and the difference is entirely about scope:

- **List-changed** — *the set* changed. `notifications/tools/list_changed` says
  "the roster of tools is different, re-fetch `tools/list`."
  `notifications/resources/list_changed` says the same for the resource
  collections. It doesn't say what changed or how — just that the list the client
  cached is no longer complete. The client's job is to ask again.

- **Subscriptions** — *this one thing* changed. A client can say "I care about
  `epicme://entries/7` specifically — tell me when *it* moves," and the server
  answers each edit with `notifications/resources/updated` for that exact URI.
  Finer-grained, and opt-in: the client only hears about what it asked to watch.

Both are the server pushing, unprompted, outside the normal answer-a-request flow.

## How the tests watch for them

Notifications don't come back as a return value — they arrive on the side channel.
The tests hook that channel with a `message_handler`, a callback the client passes
that sees every message the server pushes. Each test collects the class names of
the `ServerNotification`s that arrive, does something to the server, and asserts
the right one showed up (`ToolListChangedNotification`,
`ResourceListChangedNotification`, `ResourceUpdatedNotification`). Because
notifications are fire-and-forget, the tests sprinkle a small `anyio.sleep(0.1)`
to give the message a beat to land before checking.

## An honest note about subscriptions

List-changed has a clean high-level API — `ctx.session.send_*_list_changed()`.
Subscriptions do not, in FastMCP 1.28. There's no `@mcp.subscribe` decorator to
reach for, because FastMCP doesn't wrap resource subscriptions at all. The
subscribe/unsubscribe handlers exist — but one layer down, on the low-level
`Server` that FastMCP is built on, which you reach through `mcp._mcp_server`.
That's not a blessed public surface; it's the real answer for this feature in
this version of the SDK, and worth seeing plainly rather than papering over.

## Three steps

1. **list-changed** — a tool that registers another tool at runtime, then
   announces `tools/list_changed`.
2. **resources-list-changed** — creates fire `resources/list_changed` after they
   write. Builds on step 1.
3. **subscriptions** — register subscribe/unsubscribe on the low-level server and
   notify per-URI on edit. Builds on step 2.

Run one step at a time, from the repo root:

```sh
uv run pytest exercises/05.changes/01.problem.list-changed
```

## What's next?

This is the last topic. `mcp-fundamentals` is the only course this one builds
on, so if you came straight here, `mcp-auth` and `mcp-ui` are still waiting —
they branch off the same base and need nothing you built here.
