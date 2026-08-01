"""EpicMe MCP server — 02.tools / errors (problem).

Your job: reject a call that breaks the rules, without taking the server down.
Run `uv run pytest exercises/02.tools/03.problem.errors` until it passes.
"""

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP(
    name="epicme",
    instructions="This lets you solve math problems.",
    port=8080,
)


@mcp.tool()
def add(
    first_number: Annotated[int, Field(description="The first number to add")],
    second_number: Annotated[int, Field(description="The second number to add")],
) -> str:
    """Add two numbers together. The second number cannot be negative."""

    # The `int` hint can't catch this one: -5 is a perfectly valid integer, so
    # pydantic lets it through. Rules about *meaning* rather than *shape* live
    # here, in the function body.
    #
    # Just raise. FastMCP catches it and sends back a normal MCP response with
    # isError set — the server stays up, other clients stay connected, and only
    # this one call fails.
    #
    # Your message rides along to the model, so write it like recovery
    # instructions: say which argument is wrong and what rule it broke. The
    # model reads that and can fix its next call.
    #
    # The shape:
    #     if second_number < 0:
    #         raise ValueError("Second number cannot be negative")
    if second_number < 0:
        raise ValueError("Second number cannot be negative")
    total = first_number + second_number
    return f"The sum of {first_number} and {second_number} is {total}."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
