# Same move, resource side

The fix was one line in each create tool, right after the write:

```py
tag = db.create_tag(name, description or None)
await ctx.session.send_resource_list_changed()
```

If step 1's `send_tool_list_changed()` felt familiar, that's the point — this is
the same pattern aimed at a different list. Do the mutation, then announce that a
cached listing is stale. The client's job on receipt is to re-fetch the
`epicme://tags` or `epicme://entries` collection.

One thing worth naming: this notification fires for *creates*, which change the
collection's membership. Editing an entry's title doesn't change which entries
exist, so it isn't a list-changed event — it's about one specific resource. That
finer grain is exactly what the next step, subscriptions, is for.
