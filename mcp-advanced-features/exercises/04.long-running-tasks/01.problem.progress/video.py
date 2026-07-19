"""A tiny async stand-in for a slow "wrapped video" render.

There's no ffmpeg here and no real file ever hits disk — just a loop that
sleeps in small steps so the render *takes time* the way a real one would.
That's all we need to demonstrate the two things a long-running tool has to get
right: reporting progress as it goes, and reacting when the caller cancels
partway through.

You never need to edit this file. It's the "slow work" your tool wraps.
"""

import anyio

STEPS = 10


async def render_wrapped_video(year, mock_seconds, on_progress=None, on_cancelled=None):
    """Pretend to render a year-in-review video, in ~10 steps.

    Sleeps ``mock_seconds / STEPS`` per step and, after each step, calls
    ``await on_progress(fraction)`` where ``fraction`` climbs from 0.1 to 1.0.

    Because there's a real ``await anyio.sleep`` inside the loop, this is
    genuinely cancellable: if the surrounding task is cancelled mid-render, the
    sleep raises anyio's cancellation exception. We catch it just long enough to
    call ``on_cancelled()`` (so the caller can clean up partial work), then
    re-raise so cancellation still propagates the way anyio expects.

    Returns a fake resource uri for the finished video.
    """
    try:
        for step in range(1, STEPS + 1):
            await anyio.sleep(mock_seconds / STEPS)
            if on_progress is not None:
                await on_progress(step / STEPS)
    except anyio.get_cancelled_exc_class():
        if on_cancelled is not None:
            on_cancelled()
        raise
    return f"epicme://videos/wrapped-{year}.mp4"
