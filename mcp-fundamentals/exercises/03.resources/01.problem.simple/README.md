# Simple Resource

Let's put the journal's tags on the wire.

A static resource is a function with a URI stapled to it. The decorator carries
the URI; the function body does the lookup and returns the contents:

```python
@mcp.resource("epicme://tags")
def all_tags() -> str:
    return json.dumps([...])
```

That's genuinely it. Return a string and FastMCP wraps it in the response the
protocol expects.

## Describe it well

The keyword arguments aren't decoration — they're the entire basis on which a
client decides whether to show your resource to a user:

- `name` — a short handle, like `"tags"`
- `description` — a human sentence; this is what shows up in a picker UI
- `mime_type` — what you're actually returning. We're returning JSON, so
  `"application/json"`. Get this wrong and clients will render your JSON as
  prose.

## Why JSON?

Resource contents are text. Since a tag is structured data, serialize it:
`json.dumps(...)`. The `DB` gives you dataclasses with a `.to_dict()` helper,
which is exactly the shape `json.dumps` wants:

```python
[tag.to_dict() for tag in db.get_tags()]
```

Pass `indent=2` while you're learning — you'll be reading this output by eye in
a minute.

## Your job

Open `server.py` and register a resource at `epicme://tags` that returns every
tag in the journal as a JSON array.

```sh
uv run pytest exercises/03.resources/01.problem.simple
```

The test asks the server two things: does `epicme://tags` show up in
`resources/list`, and does reading it give back the tags? Right now the answer
to both is no.

## What's next?

Next you will move from one fixed address to a resource template. That is the
MCP counterpart to declaring a parameterized route, but the value is discovered
through `resources/templates/list` rather than assumed by a hand-written client.
