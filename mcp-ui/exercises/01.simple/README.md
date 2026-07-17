# Simple UI

So far a tool has answered the model with text — a sentence, a JSON blob, a link.
That's the right shape when a language model is the only reader. But sometimes the
reader is a person sitting in front of a UI-aware client, and a paragraph of text
is a poor way to show them a tag, an entry, a whole journal. This course is about
giving that person something to *look at*.

## What a UI resource is

The mechanism is small. A tool already returns a list of content blocks. MCP-UI
adds one more kind of block: a **UI resource** — a block that, instead of saying
"here is some text," says "render this." A UI-aware client sees it and draws
something; a plain client can ignore it and fall back to the text you sent
alongside.

You don't hand-assemble the block. `ui.py` gives you `create_ui_resource(...)`,
and your tool returns what it builds:

```py
create_ui_resource(
    uri="ui://view-tag/1",
    content={"type": "rawHtml", "htmlString": "<div><h1>home</h1></div>"},
)
```

## The `ui://` scheme

Notice the URI: `ui://view-tag/1`, not `epicme://entries/1`. That difference is
the point. An `epicme://` URI names something the client can go *fetch*. A `ui://`
URI names *this rendering* — it isn't fetchable, it's just a stable id for the
thing on screen. Two calls can reuse a URI (same widget) or vary it to force a
fresh render.

## The mimeType is the whole trick

A UI resource is your server saying "render this," and the **mimeType** is how the
client knows what "this" is. The same block shape carries an HTML string, a
DOM-building script, or a URL — and the mimeType is the one field that tells the
client which. Get comfortable with that idea now; it's the spine of every step
that follows.

This topic starts with the simplest content type there is: raw HTML. You build an
HTML string, you tag it `text/html`, and the client renders it as-is.

Run the exercise's tests from the repo root:

```sh
uv run pytest exercises/01.simple/01.problem.raw-html
```
