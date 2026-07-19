# Reporting progress

One small callback closed the gap. The render calls `on_progress(fraction)` after
each step; your callback forwards that fraction to `ctx.report_progress`, and MCP
turns it into a notification the client receives live. The tool went from a silent
block to a running commentary.

Notice the two directions in play. `render_wrapped_video` pushes progress *up* to
your tool through a plain function callback; `ctx.report_progress` pushes it *out*
to the client over the protocol. Your callback is the two-line bridge between them.
The test's ">= 2 events" check is really asking: did the client hear from the
server *during* the work, not just at the end? Now it does.
