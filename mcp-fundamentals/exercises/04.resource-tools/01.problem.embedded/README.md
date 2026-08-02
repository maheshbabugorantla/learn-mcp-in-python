# Embedded Resources

So far, you have built two kinds of MCP features:

- **Tools** perform actions, such as creating or reading a journal entry.
- **Resources** expose data through an address, such as
  `epicme://entries/1`.

If you come from REST or GraphQL, this may feel like an unusual split. A REST
`POST /entries` or a GraphQL mutation commonly returns the operation result and
the created record together. In MCP, the tool performs the action, while the
resource remains separately addressable.

That separation creates a practical question: when a tool already has the
resource data, should it return only a sentence about it, or the resource data
itself?

## The problem with returning only text

`create_entry` already receives the complete `Entry` after saving it, including
the database-assigned id. But its current result is one sentence:

```text
Entry "A quiet morning" created (id 1).
```

That sentence carries the title and the id, and nothing else. If the model wants
the mood, the content, or the tags it just stored, it has to turn around and
read `epicme://entries/1` — for data the server was holding a microsecond ago.
Returning only prose throws away structured context and buys an avoidable
round-trip.

## The MCP design

The official MCP specification allows a tool result to contain multiple content
blocks. `CallToolResult` is the response envelope, and its `content` list can
contain text, images, resource links, or embedded resources.

An embedded resource is intended to provide **additional context or data**
directly in a prompt or tool result. The client decides how to use or render it
for the model and/or the user.

Return both a human-readable summary and the resource payload:

```python
CallToolResult(
  content=[
    TextContent(
      type="text",
      text='Entry "A quiet morning" created (id 1).',
    ),
    EmbeddedResource(...),
  ]
)
```

The summary explains what happened. The embedded resource carries the data in a
form the client can use immediately.

```python
EmbeddedResource(
  type="resource",
  resource=TextResourceContents(
    uri="epicme://entries/1",
    mimeType="application/json",
    text='{"id": 1, "title": "A quiet morning", ...}',
  ),
)
```

The URI is important: it identifies the resource represented by the embedded
contents. Use the same address served by the resource template:

```python
uri=f"epicme://entries/{entry.id}"
```

This keeps the inline data connected to MCP's resource system. A client can
associate it with the resource, display it, cache it, or read a fresh copy
later. It is more than an arbitrary JSON blob.

## Embed or link?

Embed a resource when the caller has already identified the data it needs:

- `get_entry(1)` explicitly asks for entry 1.
- `create_entry(...)` creates one entry and needs to return the assigned id.

Return a resource link when the caller is choosing among many resources. For
example, embedding 200 full journal entries in `list_entries` would make the
response large even if only one entry is relevant. A link provides the URI and
metadata first; the contents can be fetched only when selected.

The design rule is simple:

- **Embed** when the context is needed now.
- **Link** when the context may or may not be needed.

The next exercise applies that rule to `list_entries`.

## Your job

`create_entry` and `get_entry` already pass their entries to the shared helper
`entry_result()`. The helper currently returns only the `TextContent` summary.

Update `entry_result()` so it returns the existing text summary first, then the
entry itself as a second block:

```python
EmbeddedResource(
  type="resource",
  resource=TextResourceContents(
    uri=f"epicme://entries/{entry.id}",
    mimeType="application/json",
    text=json.dumps(entry.to_dict(), indent=2),
  ),
)
```

All three values matter. The `uri` is the address the entry lives at, so the
client can tie the inline copy back to the resource. The `mimeType` says the
payload is JSON, so nobody has to sniff it. The `text` is the record.
`EmbeddedResource` and `TextResourceContents` both come from `mcp.types`.

Because both tools go through `entry_result()`, one change improves
`create_entry` and `get_entry` at once.

Run:

```sh
uv run pytest exercises/04.resource-tools/01.problem.embedded
```

## What’s next?

Next you will apply the opposite choice to `list_entries`: return lightweight
resource links when the model is choosing among many records. The distinction
is not a serialization trick; it is a context-delivery decision.
