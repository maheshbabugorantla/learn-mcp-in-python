# Tags the model picks

The last step appended a nice sentence. This one makes sampling do real work:
ask the model to *name tags* for a new entry, then create and attach them. The
reply stops being decoration and starts changing the database.

## Ask for something parseable

Same `create_message` call as before, but the prompt asks for structure — a short
comma-separated list — and the `system_prompt` pins the model down to exactly
that. Fill in the body of `_suggest_tags`:

```py
res = await ctx.session.create_message(
    messages=[
        SamplingMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f'Suggest 1 to 3 short tag names for this journal entry. '
                f'Title: "{entry.title}". Content: {entry.content}',
            ),
        )
    ],
    max_tokens=100,
    system_prompt="You label journal entries. Reply with ONLY 1-3 comma-separated, "
    "lowercase tag names and nothing else.",
)
text = getattr(res.content, "text", "") or ""
return [name.strip() for name in text.split(",") if name.strip()]
```

You're getting back free text, so you parse it: split on commas, strip whitespace,
drop empties. A model that ignores the format still gives you a list you can
handle instead of an exception.

## The graceful skip is already inside _suggest_tags

Unlike the simple step, here the `try/except` lives in the function you're
editing — the whole `create_message` block sits inside a `try`, and the `except`
returns `[]`. So a client that can't sample yields an empty list, the loop over it
does nothing, and the entry is created with no tags. Keep your new code inside
that `try`.

## Find-or-create, so unique names don't collide

`create_entry` takes each suggested name through `_find_or_create_tag`:

```py
def _find_or_create_tag(name: str) -> Tag:
    for tag in db.get_tags():
        if tag.name == name:
            return tag
    return db.create_tag(name)
```

Tag names are unique in the database. The model will happily suggest a tag that
already exists — `"work"` is in the seed — and blindly calling `create_tag` on it
would trip the unique constraint. Reusing the existing tag when the name matches,
and only creating when it doesn't, keeps that from happening.

## Run it

```sh
uv run pytest exercises/03.sampling/02.problem.advanced
```

## What you'll see fail

One test, `test_suggested_tags_are_created_and_attached`. The fake model returns
`"work, ideas"`. Because the unfinished `_suggest_tags` raises `NotImplementedError`
*inside* its own `try`, the `except` returns `[]` — the tool still succeeds, but no
tags get attached. The test then checks that `"ideas"` now exists as a tag and
that both `"work"` and `"ideas"` are attached to the new entry, and those
assertions fail until you make `_suggest_tags` return real names.

Stuck? Diff against `exercises/03.sampling/02.solution.advanced/server.py`.
