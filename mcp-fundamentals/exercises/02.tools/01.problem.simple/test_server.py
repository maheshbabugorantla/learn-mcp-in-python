from mcp.client import Client

from server import mcp


async def test_add_tool_is_listed():
    """The server should advertise an `add` tool with a description."""
    async with Client(mcp) as client:
        result = await client.list_tools()

    names = [tool.name for tool in result.tools]
    assert "add" in names, (
        f"The server lists no `add` tool (it lists {names}) — "
        "register one with @mcp.tool() in server.py (see the TODO)."
    )

    # `list_tools` is the first thing a client does: it's how a model finds out
    # what this server can do. The description is what it reads to decide.
    add = next(tool for tool in result.tools if tool.name == "add")
    assert add.description, (
        "The `add` tool has no description — give the function a docstring, "
        "since that's what the model reads to decide whether to call it."
    )


async def test_add_tool_adds():
    """Calling `add` should come back with the sum in a readable sentence."""
    async with Client(mcp) as client:
        result = await client.call_tool("add", {"first_number": 1, "second_number": 2})

    assert not result.is_error, (
        f"Calling `add` returned an error: {result.content[0].text}"
    )

    text = result.content[0].text
    assert "3" in text, (
        f"Expected the sum (3) somewhere in the result, but got: {text!r}"
    )
