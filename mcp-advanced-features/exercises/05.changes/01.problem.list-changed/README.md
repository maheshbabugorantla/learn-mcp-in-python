# Announce a new tool

A server's tool list isn't always fixed at startup. Sometimes a tool shows up
later — a feature flag flips, a plugin loads, the user unlocks something. When
that happens, a client that already fetched `tools/list` is holding a stale
roster, and it has no way to know a new tool is callable. The spec's answer is
`notifications/tools/list_changed`: the server saying "my tools changed, ask me
again."

## What you're building

`enable_beta_tools` is the lesson. It already registers a brand-new tool at
runtime — `mcp.add_tool(beta_ping, ...)` runs before your TODO, so `beta_ping`
becomes callable the moment the tool runs. What's missing is the nudge. Registering
a tool makes it *callable*; it does not make the client *aware*. That second half
is one line:

```py
await ctx.session.send_tool_list_changed()
```

The `🐨` block sits right after `add_tool`, with a `raise NotImplementedError`
placeholder where the notification belongs. Replace the raise with the send (and
let the real `return` run).

## What the test checks

`test_server.py` connects an in-memory client with a `message_handler` that
collects every `ServerNotification` the server pushes. It calls
`enable_beta_tools`, waits a beat (`anyio.sleep(0.1)` — notifications are
fire-and-forget), then asserts two things: that a `ToolListChangedNotification`
arrived, and that `beta_ping` now appears in `list_tools()`.

```sh
uv run pytest exercises/05.changes/01.problem.list-changed
```

## What you'll see until it's built

The `add_tool` call runs, so `beta_ping` does register — but the
`raise NotImplementedError` after it means the notification never gets sent (and
FastMCP folds the raise into an error result rather than crashing). So the first
assertion is what trips:

```
AssertionError: 🚨 enabling beta tools should send a ToolListChangedNotification...
Got notifications: []
```

An empty notification list — nothing was pushed. It fills in the moment you swap
the raise for `send_tool_list_changed()`.

Stuck? Diff against
[`01.solution.list-changed`](../01.solution.list-changed/server.py).

## What's next?

Same move, different list. Next you announce that a *collection* changed rather
than the tool roster: a client caching `epicme://entries` has no way to know that
creating a row just made its copy wrong.
