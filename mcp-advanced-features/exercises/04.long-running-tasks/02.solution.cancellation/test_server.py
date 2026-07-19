"""Cancellation test — the client changes its mind mid-render.

This one looks different from the other tests on purpose. Instead of waiting for
a result, we start a *long* render (a big `mock_seconds`) and wrap the call in
`anyio.move_on_after(0.2)`. When that timeout fires, anyio cancels the in-flight
`call_tool`, the MCP session cancels the running tool on the server, and the
render's `await` raises cancellation.

We then check two things: the client-side scope caught the cancellation
(`scope.cancelled_caught`), and the tool ran its cleanup — recorded in the
server's `LAST_CANCELLED` flag. The little sleep after the scope gives the
server task a moment to finish running its cancellation handler before we look.
"""

import anyio
from mcp.shared.memory import create_connected_server_and_client_session as connect

import server
from server import mcp


async def test_cancelling_mid_render_runs_cleanup():
    server.LAST_CANCELLED = False

    async with connect(mcp) as client:
        with anyio.move_on_after(0.2) as scope:
            # mock_seconds is much larger than the 0.2s budget, so the render is
            # still going when the timeout cancels it.
            await client.call_tool(
                "create_wrapped_video", {"year": 2026, "mock_seconds": 5.0}
            )
        # Let the server task run its on_cancelled cleanup before we assert.
        await anyio.sleep(0.2)

    assert scope.cancelled_caught, (
        "🚨 the 0.2s timeout should have cancelled the render mid-flight"
    )
    assert server.LAST_CANCELLED, (
        "🚨 the tool should run its on_cancelled cleanup when the render is cancelled"
    )
