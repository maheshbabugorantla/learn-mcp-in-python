# Listing Resources

Time for the thing that trips people up.

You now have `epicme://entries/{id}`, which serves any entry. So ask yourself:
how does a client *discover* that entry 1 exists?

Try it. Call `resources/list` and you get exactly one thing back:
`epicme://tags`. Your two templates aren't there. Call
`resources/templates/list` and you get the patterns — `epicme://entries/{id}` —
but a pattern isn't something you can read. Nobody has told the client that
`1` and `2` are real ids.

## The Python story, plainly

In the Python SDK, **a template has no `list` callback.** There is no hook where
you hand back "here are the concrete URIs this pattern expands to." Templates
appear under `resources/templates/list` and nowhere else. A template is a
*route*, not a directory listing.

(If you've seen the TypeScript SDK, this is a real difference, not something
you're missing: over there a template can carry a `list` callback that
enumerates its own instances into `resources/list`. Python has no equivalent.
Don't go hunting for it.)

## So how do records get discovered?

You add a **collection resource** — a plain static resource that returns the
list. That's the Python-native idiom:

```
epicme://entries        a static resource: here's what exists    ← discovery
epicme://entries/{id}   a template: here's how to read one       ← access
```

The pair works together. The collection answers "what's there?", the template
answers "give me that one." Have each record in the collection carry the URI
that reads it, and a client can walk straight from the list to the contents
without knowing how to build your URIs:

```python
{"id": 1, "title": "A quiet morning", "uri": "epicme://entries/1"}
```

Keep the collection lean — id, title, the URI. It's an index, not the contents.
Whoever wants the full entry can follow the URI.

## An aside: dynamic registration

There's another route. `mcp.add_resource(...)` registers a resource at runtime,
so you *could* loop over every entry and register each one as its own concrete
URI, and they'd all appear in `resources/list`.

It's rarely what you want. You'd re-register on every write, and a journal with
10,000 entries becomes a 10,000-item list response. Reach for it when you have
a small, fixed set that isn't known until startup. For records in a database,
use a collection resource.

## Your job

Add a static resource at `epicme://entries` returning each entry's `id`,
`title`, and `uri`.

```sh
uv run pytest exercises/03.resources/03.problem.list
```

## What’s next?

Next you will add completion for template arguments. The collection makes
records discoverable in principle; completion makes choosing an id practical in
the client's UI while the user is typing.
