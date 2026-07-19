# Annotate the tools

The journal works. Every tool in `server.py` registers, lists, and runs. But to a
client they're a wall of identical shapes — `get_entry` looks exactly as harmless
or as dangerous as `delete_entry`, because neither of them says anything about
what it does. Your job is to give each one a label.

## What you're adding

An annotation is a `ToolAnnotations` passed to the decorator:

```py
from mcp.types import ToolAnnotations

@mcp.tool(annotations=ToolAnnotations(title="Get Entry", readOnlyHint=True, openWorldHint=False))
def get_entry(...): ...
```

The TODO block near the top of `server.py` spells out the rules, grouped by what
each kind of tool actually does:

- **read tools** (`get_entry`, `get_tag`, `list_entries`, `list_tags`) —
  `readOnlyHint=True`, `openWorldHint=False`, plus a human `title`. They only look;
  the data they look at is this server's own closed database, not the open web.
- **delete tools** (`delete_entry`, `delete_tag`) — `destructiveHint=True`,
  `idempotentHint=True`. They remove data for good, but deleting the same id twice
  lands in the same place, so a retry is safe.
- **update tools** (`update_entry`, `update_tag`) — `idempotentHint=True`,
  `destructiveHint=False`. They overwrite fields, but re-running the same update is
  harmless.
- **create/attach tools** (`create_entry`, `create_tag`, `add_tag_to_entry`) —
  `destructiveHint=False`, plus a `title`.

Set the hints by what the tool *truly does*, not by what feels safe — the whole
point is that a client can trust them.

## What the test checks

`test_server.py` connects an in-memory client, calls `list_tools()`, and reads the
annotations back off the wire. It spot-checks the three that carry the most
weight: `get_entry` is read-only, `delete_tag` is destructive, `update_tag` is
idempotent. Annotate the whole set per the rules and those three fall out for free.

```sh
uv run pytest exercises/01.advanced-tools/01.problem.annotations
```

## What you'll see until it's built

The tools run fine right now, so nothing errors — but the tests read hints that
aren't there yet. Every assertion trips on the same thing: `annotations is None`.
That clears the moment each tool carries its `ToolAnnotations`.

Stuck? Diff against
[`01.solution.annotations`](../01.solution.annotations/server.py).
