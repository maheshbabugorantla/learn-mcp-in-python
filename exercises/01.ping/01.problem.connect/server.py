"""EpicMe MCP server — 01.ping / connect (problem).

Your job: create an MCP server and let it talk over stdio.
Run `uv run pytest exercises/01.ping/01.problem.connect` until it passes.
"""

from mcp.server.fastmcp import FastMCP

# TODO: Create the server.
#
# FastMCP takes a `name` (the machine-readable id other programs see) and an
# optional `instructions` string that tells an AI model what this server is for.
#
# Replace the `None` below with something like:
#     mcp = FastMCP(
#         name="epicme",
#         instructions="This lets you solve math problems.",
#     )
mcp = None


if __name__ == "__main__":
    # TODO: Start the server over stdio.
    #
    # stdio means this server talks over standard input/output: a client
    # launches it as a subprocess and speaks JSON-RPC through the pipes.
    # It's the transport Claude Desktop and Cursor use to run local servers.
    #
    # Call: mcp.run(transport="stdio")
    raise NotImplementedError("Start the server — see the TODO above.")
