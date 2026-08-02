# Reacting to cancellation

The progress reporting from the last step is already wired in. Now handle the
other half of a long-running tool: the caller changing its mind. When a render is
cancelled partway through, your tool should get a chance to clean up the partial
work before it goes.

## Cancellation is cooperative

You don't poll a flag or check a "should I stop?" boolean. When the caller
cancels, anyio raises its cancellation exception at the next `await` inside the
render — and `video.py` already catches it, calls `on_cancelled()`, and re-raises
so the cancellation keeps propagating. Your job is only to supply that
`on_cancelled` callback so cleanup runs on the way out:

```py
def on_cancelled() -> None:
    global LAST_CANCELLED
    LAST_CANCELLED = True

uri = await render_wrapped_video(year, mock_seconds, on_progress=on_progress, on_cancelled=on_cancelled)
```

A real tool would delete the half-written file here. Ours just flips the
module-level `LAST_CANCELLED` flag so a test can confirm the cleanup path ran. The
`CancelledError` is not yours to swallow — `video.py` re-raises it on purpose, so
the cancellation still reaches anyio the way it expects.

## This test looks different from the others

Every other test in the course awaits a result and asserts on it. This one can't —
the whole point is that the call never finishes. Instead it starts a deliberately
long render (`mock_seconds=5.0`) and wraps the call in `anyio.move_on_after(0.2)`.
When that 0.2s budget runs out, the scope cancels the in-flight `call_tool`, the
session cancels the running tool, and the render's `await` raises. A small
`anyio.sleep(0.2)` after the scope gives the server task a moment to finish its
cleanup handler before the test looks.

## Run it

```sh
uv run pytest exercises/04.long-running-tasks/02.problem.cancellation
```

## What you'll see fail

The test makes two assertions, and only the second is red. `scope.cancelled_caught`
**passes** no matter what — the timeout cancels the render whether or not you
handle it. What fails is `server.LAST_CANCELLED`: with no `on_cancelled` wired up,
the render's cleanup path never runs and the flag stays `False`. Supply the
callback and pass it to `render_wrapped_video`, and the flag flips to `True`.

Stuck? Diff against `exercises/04.long-running-tasks/02.solution.cancellation/server.py`.

## What's next?

Everything in this topic hangs off a call that is still running. **Changes** is
about the messages that don't: a tool appearing, a collection growing, a single
record edited — facts a client cached earlier and has no way to know are wrong.
