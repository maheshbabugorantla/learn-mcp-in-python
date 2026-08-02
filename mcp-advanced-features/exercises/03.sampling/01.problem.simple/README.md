# A one-line reflection

Your job: when someone creates a journal entry, ask the client's model for a
short, encouraging reflection on it and tack that onto the tool's result.

## The one call

Everything happens in `_reflect`, which `create_entry` already calls for you. Fill
in the body with a single `create_message`:

```py
res = await ctx.session.create_message(
    messages=[
        SamplingMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f'I just wrote a journal entry titled "{entry.title}". '
                "Give me a single encouraging line reflecting on it.",
            ),
        )
    ],
    max_tokens=100,
    system_prompt="You are a warm journaling companion. Reply with one short, encouraging sentence.",
)
return getattr(res.content, "text", None)
```

`create_message` sends your prompt to the client's LLM and returns a
`CreateMessageResult`. Its `.content` is a single content block — reach through it
with `getattr(res.content, "text", None)` so a missing or non-text reply becomes
`None` instead of an exception.

## You don't write the graceful skip here

Look at `create_entry`: the call to `_reflect` is already wrapped.

```py
try:
    reflection = await _reflect(ctx, entry)
except Exception:
    reflection = None
if reflection:
    result.content.append(_text(f"Reflection: {reflection}"))
```

That's the "not every client can sample" safeguard, and it's provided. A client
with no sampling support answers `create_message` with an error; that error
bubbles out of `_reflect`, gets caught here, and the entry is still created — just
without a reflection. Your only task is to make the happy path produce text.

## Run it

```sh
uv run pytest exercises/03.sampling/01.problem.simple
```

## What you'll see fail

Two tests, and only one of them is red. `test_create_entry_still_works_without_a_sampling_client`
**already passes** — the unfinished `_reflect` raises `NotImplementedError`, the
provided `try/except` swallows it, and the entry saves. That's the graceful skip
working. `test_reflection_is_appended_when_the_client_can_sample` is the one that
fails: with a fake model wired in, it expects to find `"Keep it up!"` in the
result, and there's no reflection there yet. Wire up `create_message` and it turns
green.

Stuck? Diff against `exercises/03.sampling/01.solution.simple/server.py`.

## What's next?

Next the model's answer stops being decoration. Instead of appending a sentence,
you parse what comes back into tag names and write them to the database — so a
model that answers badly no longer just reads oddly, it leaves rows behind.
