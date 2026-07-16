# Embedded Resources

Picture the round trip you have right now.

The model calls `create_entry`. Your server writes the row, gets back an `Entry`
with an id and a title and a mood, and then... returns `"Entry created."` The
model, which would quite like to know the id, has to call `resources/read` on
`epicme://entries/3` to find out what it just made. Two round-trips for data the
server was holding a microsecond ago.

An **embedded resource** closes that gap. It's a content block that carries a
resource's *full contents* inline, so the answer arrives with the answer:

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

Read that shape carefully, because it's doing two things at once. The `text` is
the data — the model can use it immediately. The `uri` is the *address* the data
came from, and it's what makes this a resource rather than a blob of JSON you
pasted into the reply. A client that wants to re-read it later, cache it, or
show it as an attachment knows exactly where it lives. Use the same URI your
`epicme://entries/{id}` template serves; you're embedding a copy of that
resource, not inventing a new one.

`TextResourceContents` is for anything textual. (Its sibling
`BlobResourceContents` takes base64 for images and the like — not today.)

## Text first, then the payload

Your tool result is a list, and order carries meaning:

```python
CallToolResult(content=[
    TextContent(type="text", text='Entry "A quiet morning" created (id 1).'),
    EmbeddedResource(...),
])
```

The sentence is for whoever is reading the conversation. The resource is for
whoever is going to *use* the entry. You want both — dropping the text leaves a
human staring at raw JSON, and dropping the resource is the problem we started
with.

## Your job

`create_entry` and `get_entry` are already written, and both hand their entry to
a single helper: `entry_result()`. It builds the text block and stops there.
Finish it — attach the entry as an embedded resource — and both tools improve at
once.

```sh
uv run pytest exercises/04.resource-tools/01.problem.embedded
```
