# Long-running tasks

Most tools answer in a blink. Some don't — rendering a "year in review" video,
crunching a report, anything that takes real seconds. A tool that just blocks and
then returns leaves the client blind the whole time: no progress bar, no sign it's
even alive, and no way to say "actually, stop."

This topic is the server keeping that conversation going while it works — the same
throughline as the rest of the course. Instead of one silent request/response, the
tool reports as it goes, and it listens for a cancel.

## The slow work is a mock

The tool wraps `render_wrapped_video` in `video.py`, and that file is a deliberate
fake. Upstream shells out to `ffmpeg`; we don't, because ffmpeg has nothing to
teach here. All the render does is loop, `await anyio.sleep` a fraction of a
second per step, and report how far along it is:

```py
for step in range(1, STEPS + 1):
    await anyio.sleep(mock_seconds / STEPS)
    if on_progress is not None:
        await on_progress(step / STEPS)
```

Because there's a real `await` in that loop, it's genuinely cancellable. If the
surrounding task is cancelled mid-render, the sleep raises anyio's cancellation
exception; the render catches it just long enough to call `on_cancelled()`, then
**re-raises** so cancellation still propagates. You never edit this file — it's the
"slow work" your tool feeds progress out of and cleans up after.

## How the tests watch

The two features are observed from opposite ends:

- **Progress** — the test passes a `progress_callback` to `call_tool`. Every time
  your tool calls `ctx.report_progress(...)`, that callback fires; the test just
  counts the events and expects several, not one final jump.
- **Cancellation** — the test wraps the call in `anyio.move_on_after(0.2)` against a
  deliberately long render. When the budget runs out, anyio cancels the in-flight
  call, the render's `await` raises, and the test checks a server-side flag to
  confirm the tool's cleanup actually ran.

Two steps, building on each other:

1. **progress** — wire the render's `on_progress` into `ctx.report_progress`.
2. **cancellation** — add an `on_cancelled` cleanup so a cancelled render tidies up.

Run each from the course root, one directory at a time:

```sh
uv run pytest exercises/04.long-running-tasks/01.problem.progress
```

Everything runs in memory — no ffmpeg, no network, nothing to start.
