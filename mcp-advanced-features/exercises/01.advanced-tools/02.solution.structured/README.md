# Return structured data

`get_entry` and `get_tag` now declare pydantic return types and return the models
directly:

```py
@mcp.tool(annotations=ToolAnnotations(title="Get Entry", readOnlyHint=True, openWorldHint=False))
def get_entry(id: int) -> EntryData:
    ...
    return EntryData(id=entry.id, title=entry.title, content=entry.content, mood=entry.mood)
```

That one change — the return annotation and the returned object — is enough for
FastMCP to derive an output schema, populate `result.structuredContent` with the
validated dict, and still emit a text-fallback block for text-only clients. You
stopped hand-assembling a `CallToolResult` and let the type carry the shape.

The annotations rode along untouched, which is the point: structured output and
annotations are independent layers. Annotations tell a client how to *treat* a
call; structured output changes what comes *back* from it. A read tool can now
announce itself as read-only, describe its result shape up front, and hand back
data a program can use without parsing prose — three things the same tool couldn't
say when it was just a function with a docstring.
