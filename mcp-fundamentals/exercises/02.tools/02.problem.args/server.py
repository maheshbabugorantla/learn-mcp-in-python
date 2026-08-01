"""EpicMe MCP server — 02.tools / args (problem).

Your job: describe the tool's arguments so the model knows what to put in them.
Run `uv run pytest exercises/02.tools/02.problem.args` until it passes.
"""

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field


mcp = FastMCP(
    name="epicme",
    instructions="This lets you solve math problems.",
    port=8080,
)


# The `int` hints below already generate the JSON Schema the model reads — that
# part is free. But the schema only says these are integers; it never says what
# they mean. Add a description to each one so the model isn't guessing.
#
# `Annotated[int, Field(description="...")]` is still an `int` as far as Python
# and your type checker are concerned — you're just attaching metadata that
# pydantic (and therefore FastMCP) picks up and puts in the schema.
#
# You'll need these two imports at the top of the file:
#     from typing import Annotated
#     from pydantic import Field
#
# The shape:
#     def add(
#         first_number: Annotated[int, Field(description="The first number to add")],
#         ...
#     ) -> str:
@mcp.tool()
def add(
    first_number: Annotated[int, Field(description="The first number to add")],
    second_number: Annotated[int, Field(description="The second number to add")]
) -> str:
    """Add two numbers together."""
    total = first_number + second_number
    return f"The sum of {first_number} and {second_number} is {total}."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
