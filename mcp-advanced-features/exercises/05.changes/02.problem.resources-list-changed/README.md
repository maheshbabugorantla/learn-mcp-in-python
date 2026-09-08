# Announce a changed collection

Tools aren't the only list a client caches. The `epicme://tags` and
`epicme://entries` resources are *collection* listings — they enumerate what's in
the journal. Every `create_tag` and `create_entry` adds a row, which makes that
cached listing wrong. This is the resource-side sibling of the last step:
`notifications/resources/list_changed`, sent the same way, for the same reason.

## What you're building

Both `create_tag` and `create_entry` are already `async` and already take a
`Context` — the plumbing is in place. After each one writes its row, fire the
notification:

```py
entry = db.create_entry(title=title, content=content, mood=mood)
await ctx.session.send_resource_list_changed()
```

Each has a `🐨` block right after the `db.create_*` call, with a
`raise NotImplementedError` placeholder standing in for the send. Replace the
raise in both tools and let the real `return` run. (`enable_beta_tools` from step
1 is still here — this step builds directly on that server; it's the tools-list
version of exactly this move.)

Note it's a single, argument-less call. `send_resource_list_changed()` doesn't
name which collection changed — like the tool version, it just says "the resource
lists are stale, re-fetch," and the client sorts out the rest.

## What the test checks

Same shape as step 1: a `message_handler` collects every `ServerNotification`.
One test creates a tag, another creates an entry, and each asserts a
`ResourceListChangedNotification` arrived (with an `anyio.sleep(0.1)` to let it
land).

```sh
uv run pytest exercises/05.changes/02.problem.resources-list-changed
```

## What you'll see until it's built

The `db.create_*` write happens, then the `raise NotImplementedError` fires
before any notification is sent. So both assertions trip on the same empty list:

```
AssertionError: 🚨 creating an entry changes the epicme://entries collection...
Got notifications: []
```

Wire `send_resource_list_changed()` into both creates and the two tests go green.

Stuck? Diff against
[`02.solution.resources-list-changed`](../02.solution.resources-list-changed/server.py).

## What's next?

"The list changed, go re-read it" is a blunt instrument when exactly one record
moved. Next you narrow it to a single URI — and drop a level while you're at it,
because FastMCP has no wrapper for subscribe and unsubscribe, so you register
those on the low-level server underneath.
