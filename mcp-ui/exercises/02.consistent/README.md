# Consistent UI

Raw HTML works, but it has a tell. You wrote `<div><h1>...</h1></div>` and styled
it however you styled it, and that's exactly what every client renders — your
fonts, your spacing, your idea of a card. Drop that into a client with its own
polished design system and it looks like a sticker someone slapped on: foreign,
off-brand, obviously not part of the app. The client can't restyle raw HTML,
because raw HTML already made every decision.

## remote-dom

The fix is to stop shipping finished markup and start shipping *instructions*.
Instead of an HTML string, this topic's content type is **remote-dom**: a small
JavaScript script that builds a UI out of the client's *own* element vocabulary —
elements like `ui-stack` and `ui-text`. Your script says "stack these, put the
tag name in this text node"; the client decides what a `ui-stack` and a `ui-text`
actually look like. Same script, native look in every client. That's the visual
consistency this topic is named for.

The elements are abstract on purpose. `ui-text` isn't an `<h1>` or a `<p>` — it's
"some text, rendered the way this client renders text." You describe structure and
content; the client owns appearance.

## The mimeType

Same wire block as before, different mimeType. remote-dom serializes to:

```
application/vnd.mcp-ui.remote-dom+javascript; framework=react
```

The `framework=react` parameter rides along in the mimeType the way
`charset=utf-8` rides along in a `Content-Type` header — it tells the client which
runtime the script expects. The client reads that mimeType, sees it's a
remote-dom script, and runs it against its own elements instead of parsing HTML.

Run the exercise's tests from the repo root:

```sh
uv run pytest exercises/02.consistent/01.problem.remote-dom
```
