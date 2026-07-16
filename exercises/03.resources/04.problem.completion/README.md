# Completions

A client showing a user `epicme://entries/{id}` has an obvious follow-up
question: okay, *which* id? Completion is how your server answers — the same
autocomplete you get from a shell when you hit tab.

## One handler for the whole server

Here's the shape to internalize:

```python
@mcp.completion()
async def handle_completion(ref, argument, context):
    ...
```

That's **one handler for the entire server** — every template, every prompt,
every argument, all funneled into a single function. So the first thing it does
is figure out what it's being asked:

- `ref` — what's being completed. A `ResourceTemplateReference` (with `.uri`,
  like `"epicme://entries/{id}"`) or a `PromptReference` (with `.name`).
  Dispatch with `isinstance`.
- `argument` — which placeholder, and what's typed so far: `argument.name` is
  `"id"`, `argument.value` is whatever the user has typed (often `""`).
- `context` — arguments already resolved, for multi-argument completions. Not
  needed here.

Return `Completion(values=[...], hasMore=False)` — or `None` when the request
isn't yours to answer. Returning `None` for things you don't handle matters:
your handler is asked about *everything*.

(Coming from the TypeScript SDK, this is a different shape. There you wrap an
individual argument in `completable()` and each one carries its own function.
Python gives you one dispatcher and you route by hand. Same protocol on the
wire — the ergonomics differ.)

## Filter by what's typed

`argument.value` is the partial input. If a user typed `2`, don't return every
id — filter:

```python
matches = [i for i in ids if i.startswith(argument.value)]
```

`"".startswith("")` is `True`, so an empty value naturally returns everything.

## One thing to know about the capability

A server only advertises completion support if a handler is registered. With no
handler at all, the client's `complete()` request doesn't come back empty — it
fails with "Method not found." That's why the test for this step reports a
missing handler rather than an empty list.

## Your job

In `server.py`, register a completion handler that suggests ids for both
templates: tag ids for `epicme://tags/{id}`, entry ids for
`epicme://entries/{id}`. Ids are ints in the DB and strings on the wire, so
`str(tag.id)`.

```sh
uv run pytest exercises/03.resources/04.problem.completion
```
