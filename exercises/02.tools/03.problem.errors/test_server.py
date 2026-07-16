from mcp.shared.memory import create_connected_server_and_client_session as connect

from server import mcp


async def test_happy_path_still_works():
    """A valid call should be untouched by the new rule."""
    async with connect(mcp) as client:
        result = await client.call_tool("add", {"first_number": 1, "second_number": 2})

    assert not result.isError, (
        f"A valid call returned an error: {result.content[0].text}"
    )
    assert "3" in result.content[0].text


async def test_negative_second_number_is_an_error():
    """A negative `second_number` should come back as a readable error."""
    async with connect(mcp) as client:
        result = await client.call_tool("add", {"first_number": 1, "second_number": -2})

    assert result.isError, (
        "Adding a negative `second_number` came back as a success "
        f"({result.content[0].text!r}) — raise a ValueError when "
        "`second_number` is negative (see the TODO in server.py)."
    )

    # FastMCP catches whatever you raise and passes your message through to the
    # client, so the model can read it and fix its next call.
    text = result.content[0].text
    assert "negative" in text.lower(), (
        f"The error came back as {text!r}, which doesn't tell the model what "
        "went wrong. Say what the rule is, e.g. "
        '"Second number cannot be negative".'
    )


async def test_the_server_survives_a_failed_call():
    """A failed tool call must not take the server down with it."""
    async with connect(mcp) as client:
        await client.call_tool("add", {"first_number": 1, "second_number": -2})

        # Same connection, right after the failure: still very much alive.
        result = await client.call_tool("add", {"first_number": 2, "second_number": 3})

    assert not result.isError, (
        f"The server stopped working after a failed call: {result.content[0].text}"
    )
    assert "5" in result.content[0].text
