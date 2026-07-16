"""EpicMe MCP server — 01.ping / connect (solution)."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="epicme",
    instructions="This lets you solve math problems.",
)


if __name__ == "__main__":
    mcp.run(transport="stdio")
