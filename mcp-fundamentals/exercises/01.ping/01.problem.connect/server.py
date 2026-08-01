"""EpicMe MCP server — 01.ping / connect (problem).

Your job: create an MCP server and let it talk over stdio.
Run `uv run pytest exercises/01.ping/01.problem.connect` until it passes.
"""

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    name="epicme",
    instructions="This lets you solve math problems.",
    port=8080,
)


if __name__ == "__main__":
    # stdio means this server talks over standard input/output: a client
    # launches it as a subprocess and speaks JSON-RPC through the pipes.
    # It's the transport Claude Desktop and Cursor use to run local servers.
    mcp.run(transport="streamable-http")
