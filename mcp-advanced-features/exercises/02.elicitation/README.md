# Elicitation

Every tool so far has been a one-way street: the client calls, your function runs
start to finish, and a result comes back. The function never gets to stop halfway
and *ask a question*. Elicitation is what happens when it needs to.

The case that makes it concrete is a destructive delete. A machine calling
`delete_entry` knows what it wants. A *person* who asked a model to "clean up my
journal" might not have meant *that* entry, and once it's gone it's gone. The
right move is to pause before the delete lands and get a yes from the human.

But the server has no direct line to the human — it talks to the client, and the
client talks to the user. Elicitation is the protocol for exactly that hop: the
server sends a structured request *back* to the client, the client collects an
answer from its user, and the answer flows back into the paused tool.

```py
class Confirm(BaseModel):
    confirmed: bool = Field(description="Whether to go ahead with the action")

result = await ctx.elicit(message="Delete this entry? This cannot be undone.", schema=Confirm)
```

Two things go out: a `message` (the human-readable question) and a `schema` (a
pydantic model describing the shape of answer you want). What comes back is an
`ElicitResult` with an `action` — did the user accept, decline, or cancel? — and,
when they accepted, `data` validated against your schema.

This is the same throughline as the rest of the course: the *server* starting a
conversation mid-flight instead of just replying. Sampling asks the model a
question; elicitation asks the user one.

## How the test fakes the user

There's no human in a test suite, so the test client supplies an
`elicitation_callback` — a stand-in user. When your tool calls `ctx.elicit(...)`,
that callback is what answers, returning a canned accept-or-decline decision. The
one exercise here runs the same delete twice: once with a user who confirms (the
row should vanish) and once with a user who declines (the row should survive).

```sh
uv run pytest exercises/02.elicitation/01.problem
```

## What's next?

**Sampling** is the same interruption pointed somewhere else. What carries over
is the discipline: both are optional client capabilities, so a server that stops
to ask has to keep working when the other side has no way to answer.
