# Reporting progress

The `create_wrapped_video` tool renders a slow video and returns its uri. Right
now it does that in total silence — the client waits, sees nothing, then gets a
result. Your job: report progress as the render works, so a client could draw a
bar.

## Bridge the render to the client

The render already knows how far along it is; it just needs somewhere to send
that. It takes an `on_progress` callback and awaits it after every step with a
fraction from `0.1` to `1.0`. Your tool's job is to define that callback so each
fraction becomes an MCP progress notification:

```py
async def on_progress(fraction: float) -> None:
    await ctx.report_progress(progress=fraction, total=1.0, message="Creating video...")

uri = await render_wrapped_video(year, MOCK_SECONDS, on_progress=on_progress)
```

`ctx.report_progress` is the outbound half — it sends a progress notification to
the client. `progress` is how far along, `total` is the finish line (`1.0`, since
the render speaks in fractions), and `message` is a human-readable status. Pass
your callback to `render_wrapped_video` as `on_progress` and the render will drive
it once per step.

## Run it

```sh
uv run pytest exercises/04.long-running-tasks/01.problem.progress
```

## What you'll see fail

The tool doesn't crash — right now it renders with no callback, finishes, and
returns the uri just fine. So the uri assertion passes. What fails is the count:
the test registers a `progress_callback`, renders, and asserts it saw at least two
progress events. With nothing wired up it sees zero. Connect `on_progress` to
`ctx.report_progress` and pass it in, and the events start flowing.

Stuck? Diff against `exercises/04.long-running-tasks/01.solution.progress/server.py`.
