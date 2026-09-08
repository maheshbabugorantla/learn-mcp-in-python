"""EpicMe MCP server — 02.tools / simple (solution)."""

from mcp.server import MCPServer

mcp = MCPServer(
    name="epicme",
    instructions="This lets you solve math problems.",
)


@mcp.tool()
def add(first_number: int, second_number: int) -> str:
    """Add two numbers together."""
    total = first_number + second_number
    return f"The sum of {first_number} and {second_number} is {total}."


if __name__ == "__main__":
    mcp.run(transport="stdio")
