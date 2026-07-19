# Confirm before deleting

The two delete tools already know they want confirmation. Look at `delete_tag`:

```py
if not await _confirmed(ctx, f'Delete tag "{tag.name}" (id {id})?'):
    return CallToolResult(content=[_text(f'Kept tag "{tag.name}" (id {id}) — deletion declined.')])
db.delete_tag(id)
```

The whole delete hinges on `_confirmed`, and right now `_confirmed` raises
`NotImplementedError`. Your job is to make it actually ask the user.

## Your task

Fill in `_confirmed` in `server.py`, following its two TODO steps. The `Confirm`
model is already defined for you:

```py
class Confirm(BaseModel):
    confirmed: bool = Field(description="Whether to go ahead with the action")
```

First, send the question to the client:

```py
result = await ctx.elicit(message=message, schema=Confirm)
```

Then read the answer back. An `ElicitResult` tells you two things — what the user
chose (`result.action`) and, if they accepted, the data they gave
(`result.data`). You want a hard yes and nothing less:

```py
return result.action == "accept" and result.data is not None and result.data.confirmed
```

Anything else — the user declined, cancelled, or accepted with `confirmed=False` —
comes back `False`, and the tool keeps the row. Delete the `NotImplementedError`
line once you're done.

Note the graceful default baked into the tool: a `False` from `_confirmed` doesn't
error, it returns a "kept it" message. So a client that can't or won't confirm
simply doesn't get the delete — the safe outcome for a destructive action.

## What the test checks

`test_server.py` connects a client wired with an `elicitation_callback` — the fake
user. It runs `delete_tag` twice:

- with a **confirming** user (`confirmed=True`): the result should say "deleted"
  and the tag should be gone from the database.
- with a **declining** user (`confirmed=False`): the result should say "kept" or
  "declined" and the tag should still be there.

```sh
uv run pytest exercises/02.elicitation/01.problem
```

## What you'll see until it's built

Until you replace it, `_confirmed` raises `NotImplementedError`, so every delete
blows up before it reaches the elicitation. The tests fail on the tool erroring
rather than on a clean accept/decline. Wire up `ctx.elicit` and both the confirm
and the decline paths light up.

Stuck? Diff against [`01.solution`](../01.solution/server.py).
