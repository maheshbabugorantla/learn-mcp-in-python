from mcp.shared.memory import create_connected_server_and_client_session as connect
from mcp.types import EmptyResult

from server import mcp


async def test_ping():
    """The server should start up and answer a ping."""
    assert mcp is not None, (
        "`mcp` is still None — create the FastMCP server in server.py (see the TODO)."
    )

    async with connect(mcp) as client:
        result = await client.send_ping()

    # A ping response is deliberately empty. Getting one back at all is the
    # point: it proves the client and server completed a handshake and are
    # speaking MCP to each other.
    assert result == EmptyResult()
