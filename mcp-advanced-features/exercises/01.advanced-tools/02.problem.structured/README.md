# Return structured data

This step picks up the annotated journal from the last one — every tool still
carries its `ToolAnnotations`, and it stays that way. What changes is the *result*
of the two read tools.

Right now `get_entry` and `get_tag` answer the way every tool has: a
`CallToolResult` holding a text block (a JSON string) and a resource link. Readable,
but a client that wants the data has to parse JSON back out of a string. Structured
output lets you hand back the data directly.

## What you're changing

The models are already defined at the top of `server.py`:

```py
class EntryData(BaseModel):
    id: int
    title: str
    content: str
    mood: str | None = None
```

Follow the TODO in `get_entry`: change its return annotation from
`-> CallToolResult` to `-> EntryData`, and return the model instead of the
hand-built result:

```py
return EntryData(id=entry.id, title=entry.title, content=entry.content, mood=entry.mood)
```

Do the same for `get_tag` with `TagData`. Leave the annotations on both decorators
exactly as they are.

## What FastMCP does with it

Once a tool declares a pydantic return type, FastMCP fills in both halves of the
response for you:

- **`result.structuredContent`** — the model as a flat, validated dict
  (`{"id": 1, "title": ..., "content": ..., "mood": ...}`), checked against an
  output schema the client can read up front.
- **a text-fallback block** — the same data rendered as text in `result.content`,
  so a client that only understands text still gets something usable.

You return one object; the client gets served whichever half it can read.

## What the test checks

`test_server.py` calls `get_entry` and `get_tag` and asserts two things about each
result: `structuredContent` equals the expected flat dict pulled straight from the
database, *and* a text-fallback block is still present alongside it.

```sh
uv run pytest exercises/01.advanced-tools/02.problem.structured
```

## What you'll see until it's built

As long as the tools return a `CallToolResult`, FastMCP has no output schema to
populate, so `structuredContent` stays `None` and the equality assertion fails.
Swap in the pydantic return types and it fills in.

Stuck? Diff against
[`02.solution.structured`](../02.solution.structured/server.py).
