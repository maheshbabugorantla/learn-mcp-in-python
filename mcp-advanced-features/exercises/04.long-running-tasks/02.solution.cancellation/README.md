# Reacting to cancellation

One `on_cancelled` callback, and the tool now shuts down cleanly instead of just
vanishing. That's the whole model of cancellation in anyio: it's cooperative. You
don't get asked politely to stop — a `CancelledError` is raised at your next
`await`, you get one chance to clean up, and then you re-raise so the cancellation
keeps travelling.

Here the pieces split neatly. `video.py` owns the catch-and-re-raise; your tool
owns the cleanup, flipping `LAST_CANCELLED` (where a real render would delete its
partial file). The tool also resets that flag to `False` at the top of each call,
so the record always reflects the run that just happened. The test proves it by
cancelling mid-render with `move_on_after` and finding the flag flipped — evidence
that the tool noticed it was cut short and tidied up before letting go.
