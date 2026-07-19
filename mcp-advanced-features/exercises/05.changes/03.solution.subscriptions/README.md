# Watching one URI

The three blocks came together as a set and a guard. Subscribe and unsubscribe
just maintain the set of watched URIs:

```py
_subscribed.add(str(uri))      # in _subscribe
_subscribed.discard(str(uri))  # in _unsubscribe
```

And the notify only fires for URIs someone actually asked about:

```py
uri = f"epicme://entries/{entry_id}"
if uri in _subscribed:
    await ctx.session.send_resource_updated(uri=AnyUrl(uri))
```

That `if` is the whole difference between subscriptions and list-changed. A
list-changed notification is a broadcast — everyone re-fetches. A resource-updated
notification is addressed: it names one URI, and it only goes out when that exact
URI is on the watch list. That's why the stays-quiet test passes for a real
reason now — entry 2 was never in `_subscribed`, so the guard skipped it.

And the part worth remembering past this exercise: all of that hung off
`mcp._mcp_server`, not `mcp`. When the high-level API doesn't cover something, the
low-level `Server` underneath it usually does — knowing it's there is the
difference between "FastMCP can't do subscriptions" and "here's where they live."
