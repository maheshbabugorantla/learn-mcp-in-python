# Tool arguments

Your `add` tool already takes two arguments, and it already works. So here's a
question worth asking: how did the model on the other end know to send
`first_number` as an integer?

## Type hints are the schema

MCP describes tool arguments with JSON Schema — a chunk of JSON saying which
arguments exist, what type each one is, and which are required. You never wrote
any. FastMCP built it by reading your type hints:

```py
def add(first_number: int, second_number: int) -> str: ...
```

becomes, over the wire:

```json
{
  "type": "object",
  "properties": {
    "first_number": { "type": "integer", "title": "First Number" },
    "second_number": { "type": "integer", "title": "Second Number" }
  },
  "required": ["first_number", "second_number"]
}
```

This is a nice payoff for a habit you probably already have. The annotations you
were writing for your editor and your type checker now do a third job: they're
the contract the model reads. And because the schema is generated from the
signature, it cannot drift out of date the way a hand-maintained one would —
change the hint, the schema changes with it.

It's enforced, too. If a model sends `"first_number": "banana"`, validation
rejects it before your function body ever runs.

## What the schema doesn't say

Look again at that JSON. It says `first_number` is an integer. It does not say
what `first_number` *means*.

For `add`, you can shrug — the name carries it. But the moment your arguments
are less obvious (`limit`? `tag_id`? `since`?), a type alone leaves the model
guessing, and a guessing model passes wrong arguments. That's where per-argument
descriptions come in:

```py
from typing import Annotated
from pydantic import Field

@mcp.tool()
def add(
    first_number: Annotated[int, Field(description="The first number to add")],
    second_number: Annotated[int, Field(description="The second number to add")],
) -> str: ...
```

`Annotated[int, ...]` still means `int` to Python and your type checker — you've
just attached extra metadata to it. FastMCP hands that off to pydantic, and the
`description` lands in the schema next to the type. Now every argument explains
itself at the exact spot where the model has to fill it in.

## Your job

Open `server.py` and give both arguments descriptions. Then:

```sh
uv run pytest exercises/02.tools/02.problem.args
```

The test calls `list_tools()` and reads the generated schema — the same view the
model gets.
