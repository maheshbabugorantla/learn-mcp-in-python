# Resource Templates

`epicme://tags` gives you the whole list. But a client usually wants *one*
thing: this tag, that entry. You could register a resource per record, but the
journal grows and the URIs would have to be re-registered every time someone
writes something down.

A **resource template** solves this. Put a placeholder in the URI and you've
described a family of resources with one function:

```python
@mcp.resource("epicme://tags/{id}")
def one_tag(id: str) -> str:
    ...
```

Now `epicme://tags/1`, `epicme://tags/2`, and `epicme://tags/47` all route to
`one_tag`, with `id` filled in from the URI.

## The rule that will bite you

**The placeholder name must exactly match the parameter name.** `{id}` in the
URI means the function takes `id`. If they disagree, FastMCP raises immediately
at import time — your server won't even start. That's a feature: it's a typo
caught at import instead of a confusing 404 at runtime.

Also note `id` arrives as a **string**, always — it was parsed out of a URI.
The DB wants an int, so cast it: `db.get_tag(int(id))`.

## Missing records

`db.get_tag(999)` returns `None`. It doesn't raise. So you have to:

```python
if tag is None:
    raise ValueError(f"Tag with ID '{id}' not found")
```

Raise, don't return `None` or an error dict. FastMCP catches the exception and
turns it into a proper MCP protocol error, so the client learns the read
failed rather than cheerfully handing the model the string `"null"`. Put the id
in the message — the person debugging this will thank you.

## Your job

In `server.py`, register two templates:

- `epicme://tags/{id}` — one tag
- `epicme://entries/{id}` — one entry (its `.to_dict()` includes its tags)

```sh
uv run pytest exercises/03.resources/02.problem.template
```

Watch where these show up. Templates are listed under
`resources/templates/list`, **not** `resources/list` — that difference is the
whole subject of the next step.

## What's next?

Next you will solve the other half of the problem: a template explains how to
read an item, but it does not enumerate which ids exist. A collection resource
will provide that index so clients can discover real records instead of guessing
URI values.
