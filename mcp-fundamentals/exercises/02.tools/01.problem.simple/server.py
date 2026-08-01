"""EpicMe MCP server — 02.tools / simple (problem).

Your job: register your first tool.
Run `uv run pytest exercises/02.tools/01.problem.simple` until it passes.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="epicme",
    instructions="This lets you solve math problems.",
    port=8080,
)


# TODO: Register an `add` tool.
#
# `@mcp.tool()` turns a plain Python function into something an AI model can
# call. FastMCP reads the function to build the tool: the function's name
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

@mcp.tool(title="Add Two Integer numbers", description="first_number: int + second_number: int -> result: str")
def add(first_number: int, second_number: int) -> str:
    """ Add two numbers """
    result = first_number + second_number
    return f"The sum of {first_number} and {second_number} is {result}"


@mcp.tool(title="Add Two Floating Point numbers", description="first_number: float + second_number: float -> result: float")
def add_floats(first_number: float, second_number: float) -> float:
    """ Add two floating point numbers """
    result = first_number + second_number
    return float(f"{result:.4f}")



if __name__ == "__main__":
    mcp.run(transport="streamable-http")
