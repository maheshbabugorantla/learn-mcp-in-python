# Advanced tools

A tool, as you left it in the fundamentals course, is a name, a description, an
argument schema, and a function that runs. That's enough for a model to call it.
It is not enough for a client to be *careful* with it, or to do anything with the
result besides read it back as prose. This topic closes both gaps.

## Annotations: metadata a client can act on

Look at the base journal's dozen tools through the client's eyes. `get_entry`
reads. `update_tag` overwrites. `delete_entry` destroys. Over the wire they are
indistinguishable — same shape, same silence about what they *do*. A client that
wants to put a confirmation dialog in front of the dangerous ones has no way to
tell which ones are dangerous.

Annotations are that missing signal. Each tool can carry a `ToolAnnotations`: a
human-readable `title` plus a handful of advisory hints.

```py
from mcp.types import ToolAnnotations

@mcp.tool(annotations=ToolAnnotations(title="Delete Entry", destructiveHint=True, idempotentHint=True))
def delete_entry(...): ...
```

The hints are a small, fixed vocabulary:

- **readOnlyHint** — the tool doesn't change anything. Safe to call freely, safe
  to call speculatively.
- **destructiveHint** — the tool can remove or overwrite data. Worth a
  confirmation before it runs.
- **idempotentHint** — calling it twice lands the same result as calling it once.
  Safe to retry after a dropped connection.
- **openWorldHint** — the tool reaches outside the server (the open web, another
  service) rather than a closed, known dataset like this journal's database.

The word *hint* is load-bearing. None of these change what your function does;
they don't validate anything or block a call. They are how a tool describes its
own behaviour so a client — or the model driving it — can decide how much ceremony
a call deserves *without having to call it and find out.*

## Structured output: a result that's also data

The base journal answers every read with a `CallToolResult` full of text: a
human-friendly sentence plus, if you squint, a JSON string buried in a text block.
A model can read that. A program that wants the actual `id` has to fish the JSON
back out of a string and hope the format holds.

Give a tool a pydantic return type instead and FastMCP fills in *both* halves of
the response:

```py
class EntryData(BaseModel):
    id: int
    title: str
    content: str
    mood: str | None = None

@mcp.tool()
def get_entry(id: int) -> EntryData:
    ...
    return EntryData(id=entry.id, title=entry.title, content=entry.content, mood=entry.mood)
```

Now the result carries `structuredContent` — the data as a real, validated dict,
matching an output schema the client can read up front — *and* a text-fallback
block, so a client that only understands text still gets something readable. One
return value, both audiences served.

## Two steps

1. **annotations** — add a `ToolAnnotations` to every tool so a client can tell
   the readers from the writers from the destroyers.
2. **structured** — give the two read tools pydantic return types so their results
   arrive as machine-readable data, not just prose. It builds directly on the
   annotated server from step 1.

Run each step's tests from the repo root, one directory at a time:

```sh
uv run pytest exercises/01.advanced-tools/01.problem.annotations
```
