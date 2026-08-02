# Resource Tools

Two topics ago you wrote tools. One topic ago you wrote resources. This topic
is about the seam between them, and it hangs on a single question:

**what is a tool actually allowed to return?**

So far, always a string. `add` returned `"The sum of 1 and 2 is 3."` and that
string became the entire result. That works, but it quietly throws something
away. When `create_entry` saves a journal entry, the server *has* the entry —
the whole record, id and all, sitting right there. Squashing it into prose
means the model gets a sentence about the data instead of the data.

A tool result isn't a string. It's a **list of content blocks**, and text is
only one kind. Two of the others are the point of this topic:

- an **embedded resource** — the resource's full contents, inline, right now
- a **resource link** — a URI pointing at a resource, to be fetched if wanted

Same journal, same database, same URIs you built in the last topic. The only
thing changing is what comes back out of a tool call.

## Returning a `CallToolResult`

To control the content list you return a `CallToolResult` instead of a `str`:

```python
from mcp.types import CallToolResult, TextContent

@mcp.tool()
def my_tool() -> CallToolResult:
    """Something useful."""
    return CallToolResult(content=[TextContent(type="text", text="hello")])
```

That's the escape hatch. Returning a plain string is FastMCP wrapping it in
exactly this shape for you; returning the `CallToolResult` yourself just means
you decide what goes in the list. You can put several blocks in, in any order —
a sentence for the human reading the transcript, then the structured payload.

Everything else you already know still applies. `raise ValueError("...")` still
produces an error result. Your resources and your completion handler carry
forward untouched.

Two steps:

1. **Embedded resources** — `create_entry` and `get_entry` hand back the full
   entry inline.
2. **Resource links** — `list_entries` hands back URIs instead of contents.

The interesting part is step 2, where you have to decide which one a given tool
deserves.

This is the point where MCP's primitives start to compose rather than resemble
separate endpoint categories. The model chooses the tool, the application can
load resources, and the tool result can carry resource context across that
boundary. The next exercises make that choice concrete: inline context for one
known record, then a link when the result is a selection among many records.

## What’s next?

After both steps, **Prompts** hands control to a third party: the person using
the client. They pick a prompt from a menu, and the server answers with messages
that can carry the same embedded resources you build here.
