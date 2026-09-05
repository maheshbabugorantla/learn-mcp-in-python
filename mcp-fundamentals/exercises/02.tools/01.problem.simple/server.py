"""EpicMe MCP server — 02.tools / simple (problem).

Your job: register your first tool.
Run `uv run pytest exercises/02.tools/01.problem.simple` until it passes.
"""

from mcp.server import MCPServer

mcp = MCPServer(
    name="epicme",
    instructions="This lets you solve math problems.",
)


# TODO: Register an `add` tool.
#
# `@mcp.tool()` turns a plain Python function into something an AI model can
# call. MCPServer reads the function to build the tool: the function's name
# becomes the tool's name, and its docstring becomes the description the model
# uses to decide whether this tool is what it needs. Write that docstring for
# the model, not for your teammates.
#
# Return a full sentence rather than a bare number — the reader on the other end
# is a language model, and "The sum of 1 and 2 is 3." is a lot harder to
# misread than "3".
#
# The shape:
#     @mcp.tool()
#     def add(first_number: int, second_number: int) -> str:
#         """Add two numbers together."""
#         return f"The sum of ... is ..."


if __name__ == "__main__":
    mcp.run(transport="stdio")
