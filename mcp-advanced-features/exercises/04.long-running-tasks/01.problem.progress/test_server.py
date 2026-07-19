"""Progress tests — a fake client that collects the tool's progress updates.

`client.call_tool(..., progress_callback=...)` registers a callback that fires
every time the server calls `ctx.report_progress(...)`. We render a (fast, fake)
wrapped video and check two things: the tool still returns the video's uri, and
it reported progress along the way — not one final jump, but several steps.
"""

from mcp.shared.memory import create_connected_server_and_client_session as connect

from server import mcp


async def test_reports_progress_and_returns_the_uri():
    events: list[tuple[float, float | None, str | None]] = []

    async def on_progress(progress: float, total: float | None, message: str | None):
        events.append((progress, total, message))

    async with connect(mcp) as client:
        result = await client.call_tool(
            "create_wrapped_video", {"year": 2026}, progress_callback=on_progress
        )

    assert not result.isError, f"🚨 the tool should succeed. Got: {result.content!r}"

    # The uri can show up in a text block or a resource link — accept either.
    text = " ".join(c.text for c in result.content if c.type == "text")
    links = " ".join(str(c.uri) for c in result.content if c.type == "resource_link")
    haystack = f"{text} {links}"
    assert "epicme://videos/wrapped-2026.mp4" in haystack, (
        f"🚨 the result should contain the finished video's uri. Got: {haystack!r}"
    )

    assert len(events) >= 2, (
        f"🚨 the tool should report progress as it renders (expected >= 2 updates). "
        f"Got {len(events)}: {events!r}"
    )
