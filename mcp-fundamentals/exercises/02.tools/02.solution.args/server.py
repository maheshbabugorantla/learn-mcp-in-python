"""EpicMe MCP server — 02.tools / args (solution)."""

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP(
    name="epicme",
    instructions="This lets you solve math problems.",
)


@mcp.tool()
def add(
    first_number: Annotated[int, Field(description="The first number to add")],
    second_number: Annotated[int, Field(description="The second number to add")],
) -> str:
    """Add two numbers together."""
    total = first_number + second_number
    return f"The sum of {first_number} and {second_number} is {total}."


if __name__ == "__main__":
    mcp.run(transport="stdio")
