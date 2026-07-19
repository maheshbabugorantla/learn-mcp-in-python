# Confirm before deleting

`_confirmed` is now the whole feature in two lines:

```py
async def _confirmed(ctx: Context, message: str) -> bool:
    result = await ctx.elicit(message=message, schema=Confirm)
    return result.action == "accept" and result.data is not None and result.data.confirmed
```

`ctx.elicit` is the round trip: your question and its `Confirm` schema go out to
the client, execution of the tool suspends, and it resumes with an `ElicitResult`
once the user answers. Elicitation is a structured request *back* to the client —
not a log line, not a prompt you print, but a real request the client is expected
to answer, with a schema saying what a valid answer looks like.

The `and` chain is deliberately strict. `result.action` can be `accept`,
`decline`, or `cancel`, and only `accept` is worth reading further; even then you
confirm `result.data` arrived and that `confirmed` is truthy. Three ways to say no,
one way to say yes — the correct bias for something irreversible.

That strictness also handles the client that *can't* elicit. A client without the
`elicitation` capability won't sit and answer, and a tool that blocked forever
waiting would deadlock. Because anything short of an explicit yes returns `False`,
and because the delete tools treat `False` as "keep it and report that," the
ungraceful case degrades into the safe one: no confirmation, no delete, a clear
message instead of a hang.
