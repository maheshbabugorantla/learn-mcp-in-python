# Your first prompt

Your job: register a `suggest_tags` prompt that a person can pick from a menu.

## Registering it

Same shape as everything else in this course — a decorator on a plain function:

```py
@mcp.prompt(
    name="suggest_tags",
    description="Suggest tags for a journal entry",
)
def suggest_tags(entry_id: str) -> str:
    return f"Look up the journal entry with ID {entry_id} and suggest tags for it."
```

Return a string and it becomes a single user message — the opening line of the
conversation, as if the user had typed it themselves.

## The description is a menu item

With a tool, the description is read by a *model* deciding whether to call it.
With a prompt, the description is read by a *person* scanning a list. Write it
like a menu item, not a function name: "Suggest tags for a journal entry", not
`suggest_tags(entry_id)`.

## Arguments are always strings

This one catches people out. Prompt arguments arrive as **strings**, always, no
matter what you annotate:

```py
await client.get_prompt("suggest_tags", {"entry_id": "1"})
```

That's the protocol, not a FastMCP quirk — the client is rendering a text input
and sending you what the user typed. So take a `str` and convert inside your
function if you need a number. Annotate it `int` and you're writing a promise the
wire can't keep.

As with tools, `Annotated[str, Field(description=...)]` gives the argument a
description, which is the label the client shows above its input box:

```py
entry_id: Annotated[
    str, Field(description="The ID of the journal entry to suggest tags for")
],
```

## Notice what's missing

Read the prompt text you're about to write and notice what it's really doing: it
*asks the model to go look things up*. Find the entry. Then find the tags. That's
two round trips before any thinking starts, and the model has to guess the right
URIs to read.

It works. It's also wasteful, and the next exercise fixes it. Get this one
working first — but keep that itch.

## Your task

Open `server.py` and follow the TODO. Then:

```sh
uv run pytest exercises/05.prompts/01.problem.prompts
```

Stuck? Diff against `exercises/05.prompts/01.solution.prompts/server.py`.
