from mcp.shared.memory import create_connected_server_and_client_session as connect

from server import mcp


async def get_add_tool():
    """Fetch the `add` tool exactly the way a real client would."""
    async with connect(mcp) as client:
        result = await client.list_tools()

    names = [tool.name for tool in result.tools]
    assert "add" in names, (
        f"The server lists no `add` tool (it lists {names}) — "
        "it should still be registered with @mcp.tool() in server.py."
    )
    return next(tool for tool in result.tools if tool.name == "add")


async def test_type_hints_generate_the_schema():
    """The `int` hints alone should produce a typed, required schema."""
    add = await get_add_tool()
    properties = add.inputSchema.get("properties", {})

    for name in ("first_number", "second_number"):
        assert name in properties, (
            f"The schema has no `{name}` argument (it has {list(properties)}). "
            "FastMCP builds this from the function signature, so keep both "
            "arguments named as they were."
        )
        assert properties[name].get("type") == "integer", (
            f"`{name}` should show up as an integer in the schema, but it's "
            f"{properties[name].get('type')!r}. That comes straight from the "
            "`int` type hint — keep it annotated as an int."
        )

    assert set(add.inputSchema.get("required", [])) == {"first_number", "second_number"}


async def test_arguments_describe_themselves():
    """Each argument should carry a description the model can read."""
    add = await get_add_tool()
    properties = add.inputSchema.get("properties", {})

    for name in ("first_number", "second_number"):
        # `.get` rather than `[...]` on purpose: before you do the TODO there is
        # no description key at all, and a friendly failure beats a KeyError.
        description = properties.get(name, {}).get("description", "")
        assert description, (
            f"`{name}` has no description in the schema — wrap it in "
            f'Annotated[int, Field(description="...")] in server.py '
            "(see the TODO)."
        )
