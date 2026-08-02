# Completing a prompt argument

Your job: make the `entry_id` argument suggest real ids.

## The gap

Your prompt asks for an `entry_id`. A person picking it from a menu sees an empty
text box and is expected to know that entry 3 is the one about the fog. Nobody
knows that. They'd have to go list the entries, find the id, come back, and type
it — which is exactly the busywork this prompt was supposed to save.

You already fixed this for resource templates in `03.resources`. Same idea here.

## One handler, two kinds of ref

You have a completion handler already, and this is the thing to notice: **there
is only one for the whole server.** It isn't attached to the prompt or to the
template. So its first job is always to work out *what* is being completed:

```py
@mcp.completion()
async def handle_completion(ref, argument, context) -> Completion | None:
    if isinstance(ref, PromptReference):
        ...        # a prompt argument
    if isinstance(ref, ResourceTemplateReference):
        ...        # a {slot} in a template URI
```

`ref` tells you which. Then `argument.name` tells you *which* argument, and
`argument.value` is what the user has typed so far — filter on it:

```py
ids = [str(entry.id) for entry in db.get_entries()]
matches = [id for id in ids if id.startswith(argument.value)]
return Completion(values=matches, hasMore=False)
```

Note `hasMore`, not `has_more` — these types carry the protocol's camelCase names.

## Returning None is a real answer

For any ref or argument you don't recognize, return `None`. That means "no
suggestions for this one", which is always a fine answer and much better than
raising. Your handler will be asked about things you didn't write; a `None` at
the bottom is the graceful way to say so.

## If you know TypeScript, this looks different

Worth flagging, since this course is a port. TypeScript attaches a `complete`
callback to each argument individually. Python gives you one dispatcher for the
entire server, and you branch inside it. Same capability, different shape — if
you go read the TypeScript docs, don't go hunting for a per-argument hook here.

## Your task

Open `server.py` and follow the TODO. Then:

```sh
uv run pytest exercises/05.prompts/03.problem.completion
```

Stuck? Diff against `exercises/05.prompts/03.solution.completion/server.py`.

When it's green, you're done — read `exercises/05.prompts/FINISHED.md`.

## What’s next?

This closes the fundamentals sequence: a persistent MCP peer exposes bounded
model actions, application-selected context, and user-selected guidance. The
next course can build on that contract with authentication, richer workflows,
and UI concerns rather than re-teaching the protocol primitives.
