# Notify one specific resource

List-changed says "the *set* changed — re-fetch the list." Subscriptions are
finer: a client says "I care about this *one* resource, tell me when *it*
changes," and the server answers each edit with `notifications/resources/updated`
for that exact URI. The client only hears about what it opted into.

## The honest part: this drops to the low-level server

FastMCP 1.28 doesn't wrap subscriptions. There's no `@mcp.subscribe` decorator,
because FastMCP has no high-level surface for this feature at all. The
subscribe/unsubscribe handlers do exist — they just live one layer down, on the
low-level `Server` that FastMCP is built on, which you reach through
`mcp._mcp_server`:

```py
@mcp._mcp_server.subscribe_resource()
async def _subscribe(uri: AnyUrl) -> None:
    _subscribed.add(str(uri))

@mcp._mcp_server.unsubscribe_resource()
async def _unsubscribe(uri: AnyUrl) -> None:
    _subscribed.discard(str(uri))
```

That's not a blessed public API — it's the real answer in this SDK version, and
it's what FastMCP delegates to underneath anyway. `_subscribed` is a plain
module-level `set[str]` of the URIs some client asked to watch.

## What you're building

Three `🐨` blocks, all wiring the same set:

1. `_subscribe` — remember the URI: `_subscribed.add(str(uri))`.
2. `_unsubscribe` — forget it: `_subscribed.discard(str(uri))`.
3. `_notify_entry_changed` — only notify if this URI is actually watched, then
   send the per-URI update:

```py
uri = f"epicme://entries/{entry_id}"
if uri in _subscribed:
    await ctx.session.send_resource_updated(uri=AnyUrl(uri))
```

`update_entry` and `delete_entry` already call `_notify_entry_changed(ctx, id)`
after they touch the row — an edit and a deletion are both things a subscriber
asked to hear about (after a delete, their next fetch will 404). You're filling in
the handlers and the notify body; the call sites are done. The first two blocks
are `pass`; the third is a `raise NotImplementedError`.

## What the test checks

Two tests, both via a `message_handler`. The first subscribes to
`epicme://entries/1`, updates entry 1, and asserts a `ResourceUpdatedNotification`
arrived — it collects notification *types*, so it never inspects the URI. The
second is what actually proves your filter works: it subscribes to entry 1 but
updates entry 2 — nobody is watching 2 — and asserts the server stays quiet.

```sh
uv run pytest exercises/05.changes/03.problem.subscriptions
```

## What you'll see until it's built

`_notify_entry_changed` raises, so updating the subscribed entry never notifies:

```
AssertionError: 🚨 updating a subscribed entry should send a ResourceUpdatedNotification
for epicme://entries/1. Got notifications: []
```

The stays-quiet test *passes right now* — but only vacuously: nothing notifies
yet, so of course the unsubscribed entry is silent. It only becomes a real check
once you've wired the notify and the subscribed URI set. When both are in place,
the subscribed-update test goes green and the stays-quiet test stays green for the
right reason — because `if uri in _subscribed` filtered entry 2 out.

Stuck? Diff against
[`03.solution.subscriptions`](../03.solution.subscriptions/server.py).

## What's next?

That's the last exercise in the course. Read
`exercises/05.changes/FINISHED.md` — it names the throughline running under all
five topics, and it is straight about what this course simplified on purpose,
which is the part worth knowing before you build the real thing.
