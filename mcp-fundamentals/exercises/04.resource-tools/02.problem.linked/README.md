# Resource Links

Embedding was such a clear win in the last step that the obvious move is to do
it everywhere. Let's see where that goes.

`list_entries` returns every entry in the journal. Embed them all and a journal
with 200 entries returns 200 full records — every body, every field — so the
model can read the titles and pick one. It pays for all 200 to use one. And
context isn't just money, it's attention: bury the answer in noise and the
answer gets harder to find.

A **resource link** is the other option. It hands back the *address* instead of
the contents:

```python
ResourceLink(
    type="resource_link",
    uri="epicme://entries/1",
    name="entry-1",
    title="A quiet morning",
    description="Journal entry: A quiet morning",
    mimeType="application/json",
)
```

No `text` field — that's the whole idea. The contents stay on the server until
somebody asks. `name` is required and acts as a short handle; `title` is the
human-readable label. Include it. `epicme://entries/7` tells nobody anything,
and a link nobody can identify is a link nobody can choose.

Then the model picks one and calls `get_entry(1)` — which, thanks to the last
step, embeds it. The pair works: browse cheaply, then fetch exactly what's
needed.

## So which one?

The question isn't "which is better," it's **"will this get used?"**

| | Embed | Link |
|---|---|---|
| Contents | inline, right now | fetched on demand |
| Costs context | always | only if followed |
| Extra round-trip | never | if followed |

- **Embed** when you know the data is needed *now*, and there's one of it.
  `get_entry(1)` — they asked for it by id. Don't make them ask twice.
- **Link** when the caller is choosing, or when the list could be long.
  `list_entries` — most of those entries will never be opened.

The `mimeType` on a link is a small kindness: it says what a client would be
fetching before it commits to fetching it.

## Your job

Fill in `list_entries` so it returns a `ResourceLink` per entry instead of only
a count. Leave `create_entry` and `get_entry` embedding — that's the right call
for both.

```sh
uv run pytest exercises/04.resource-tools/02.problem.linked
```

## What’s next?

Next, **Prompts** moves control to the person using the client. You will package
expert guidance as a user-selected template, then reuse embedded resources to
give the model the context it needs without making it rediscover known data.
