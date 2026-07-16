# Resource Templates (solution)

Two templates now serve every tag and every entry. The `{id}` placeholder
matches the `id` parameter exactly — FastMCP would have raised at import time
otherwise — and it arrives as a string, so both bodies cast with `int(id)`.

Both raise `ValueError` when the record is missing, because `db.get_tag()` and
`db.get_entry()` return `None` rather than raising. FastMCP turns that
exception into a proper MCP error for the client.

Try `list_resources()` against this server and you'll see only `epicme://tags`.
The templates aren't there. That's the next step.

The lesson is in [02.problem.template](../02.problem.template/README.md).
