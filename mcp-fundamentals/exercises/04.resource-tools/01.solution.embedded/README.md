# Embedded Resources (solution)

`entry_result()` now returns two blocks — the sentence, then the entry — and
because both tools funnel through it, `create_entry` and `get_entry` both got
better from one edit. That's worth noticing: "how do we hand back an entry" is a
decision, and decisions want one home.

The `uri` on the `TextResourceContents` is the part that's easy to treat as
decoration. It isn't. It's what ties this copy back to
`epicme://entries/{id}` — the same resource, delivered early. A client can cache
it under that key, offer it as an attachment, or re-read it later for a fresh
copy. Invent a different URI here and you've silently created a second, unrelated
resource that nothing can follow up on.

Note what *didn't* change. The resources still work. The completion handler still
works. `raise ValueError(...)` still produces an error result — returning a
`CallToolResult` yourself doesn't opt you out of any of that, it just means you
choose what goes in the content list.

One caution, and it's the setup for the next step: embedding is not free. Every
byte lands in the model's context whether it gets used or not. One entry is
nothing. A hundred entries is a bill.

The lesson is in [01.problem.embedded](../01.problem.embedded/README.md).
