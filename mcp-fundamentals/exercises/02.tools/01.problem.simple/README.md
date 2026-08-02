# Your first tool

Right now the server starts, handshakes, and answers a ping. It cannot *do*
anything. Let's give it a tool.

## What a tool actually is

A tool is a Python function you hand to the server. The server advertises it to
any connected client, and an AI model on the other end can decide to call it. You
register one with a decorator:

```py
@mcp.tool()
def add(first_number: int, second_number: int) -> str:
    """Add two numbers together."""
    return f"The sum of {first_number} and {second_number} is {first_number + second_number}."
```

That's it. No schema file, no registration table, no separate manifest to keep in
sync. FastMCP reads the function itself: the name becomes the tool's name, and
the docstring becomes the description.

## Why the docstring matters more than usual

Get used to this idea early, because it runs through the whole topic: **the
docstring is not a comment for your teammates. It is the prompt.**

When a model is deciding whether to call your tool, the description is most of
what it has to go on. A model that sees `"""Add two numbers together."""` knows
when `add` is the right move. A model that sees no description at all is left
guessing from the bare name — and it will guess, sometimes badly. Vague
descriptions produce tools that get called at the wrong moment, or never get
called at all.

So write the docstring for the model. Say what the tool does, plainly.

## Returning a sentence, not a number

Notice the example returns `"The sum of 1 and 2 is 3."` rather than `3`. That's
deliberate. The thing reading your return value is a language model, and a bare
`3` arriving with no context is easy to misattribute — was that the sum, or a
leftover from some other call? A self-describing sentence is unambiguous. Tool
results are conversation, so write them like it.

## Your job

Open `server.py` and register an `add` tool. Then:

```sh
uv run pytest exercises/02.tools/01.problem.simple
```

The test asks the server to list its tools, then calls yours — the same two
moves a real client makes.

## What’s next?

Your type hints already became the JSON Schema the model reads. Next you will
look at what that schema still doesn't say, and describe each argument so it
explains itself at the exact spot the model has to fill it in. The signature is
about to become more than an implementation detail: it becomes part of the
model-facing contract.
