# Initial render data

An `externalUrl` resource points an iframe at a page your server hosts. But that
page starts out empty — so how does it get the data it's supposed to show?

The obvious answer is: it fetches it. Point the iframe at
`/ui/entry-viewer?id=7`, and let the page turn around and ask the server for
entry 7. That works, but it's a second round trip for something you *already had
in hand* when you built the resource. You looked the entry up to know it exists;
now the page is looking it up again.

## Hand the data over up front

There's a better shape. When your tool returns the resource, it can attach the
data as metadata — `initial-render-data` — and the host passes that straight into
the frame before its first paint. No fetch, no query string, no round trip. The
page renders from data it was handed.

That changes the URL, too. If the entry travels in `_meta`, the URL doesn't need
to identify anything — it's the same generic `/ui/entry-viewer` page every time.
The address stops carrying state; the metadata carries it instead.

## The two halves

- **The graded half** (this topic's exercise) is server-side: `view_entry(id)`
  builds an `externalUrl` resource whose `ui_metadata` carries the entry as
  `initial-render-data`. That's Python, and the tests assert its exact wire
  shape.

- **The consuming half** is in the browser, in the demo. The entry-viewer page
  calls `waitForRenderData()` — it announces it's ready and waits for the host to
  hand it the entry, then renders with no fetch at all. You met that function in
  topic 04; now you'll see what feeds it.

## A note on tool results

The demo also shows a related idea worth naming: a `tool` message an iframe posts
up can come back with a **result** the host received from the tool call. It's the
same postMessage conversation from topic 04, just carrying data back down. You
don't build anything for it here — watch it in the demo's message log when you
click **View entry** — but it rounds out the picture: data flows both ways across
that frame boundary.

Run this topic's exercise from the `mcp-ui` directory:

```sh
uv run pytest exercises/05.advanced/01.problem.render-data
```

## What's next?

This is the last topic, and the exercise below is the last graded step. After it,
`mcp-auth` and `mcp-advanced-features` branch off the fundamentals course in
either order — neither one needs anything you built here.
