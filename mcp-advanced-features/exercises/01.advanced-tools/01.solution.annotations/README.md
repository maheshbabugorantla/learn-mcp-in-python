# Annotate the tools

Every tool now carries a `ToolAnnotations`, and `list_tools()` hands those hints
to the client alongside the name and schema:

```py
@mcp.tool(annotations=ToolAnnotations(title="Delete Tag", destructiveHint=True, idempotentHint=True))
def delete_tag(...): ...
```

Nothing about how the tools *run* changed — `delete_tag` deletes exactly as it did
before. What changed is that the client can now see it coming. That's the entire
value of an annotation: it moves knowledge that used to live only inside your
function out to the caller, before the call.

Why that matters comes down to who reads the hints and what they do with them. A
client can render your read-only tools without a warning and gate your destructive
ones behind a confirmation. A model deciding which tool to reach for can prefer the
`readOnlyHint=True` ones when it's just gathering context, and treat
`destructiveHint=True` as a reason to pause and ask. An idempotent tool is one a
client can safely retry after a dropped connection; a non-idempotent one isn't.

None of this is enforced — the hints are advisory, and a client is free to ignore
them. But a well-behaved client leans on them constantly, and a tool that lies
about its own behaviour (a destructive tool marked read-only) is worse than one
with no hints at all. Describe what the tool actually does, and the client can be
careful on your behalf.
