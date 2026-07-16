"""EpicMe MCP server — 03.resources / list (problem).

Your job: make individual entries discoverable with a collection resource.
Run `uv run pytest exercises/03.resources/03.problem.list` until it passes.
"""

import json

from mcp.server.fastmcp import FastMCP

from db import DB

mcp = FastMCP(
    name="epicme",
    instructions="This lets you read and manage a personal journal.",
)
db = DB()
db.seed()


@mcp.resource(
    "epicme://tags",
    name="tags",
    description="All tags in the journal",
    mime_type="application/json",
)
def all_tags() -> str:
    tags = [tag.to_dict() for tag in db.get_tags()]
    return json.dumps(tags, indent=2)


@mcp.resource(
    "epicme://tags/{id}",
    name="tag",
    description="A single tag by ID",
    mime_type="application/json",
)
def one_tag(id: str) -> str:
    tag = db.get_tag(int(id))
    if tag is None:
        raise ValueError(f"Tag with ID '{id}' not found")
    return json.dumps(tag.to_dict(), indent=2)


# TODO: Register a collection resource at `epicme://entries`.
#
# The `epicme://entries/{id}` template below can serve any entry, but it only
# ever appears under `resources/templates/list` — a pattern, not a list of what
# exists. Python templates have no `list` callback, so this static resource is
# how a client discovers that entries 1 and 2 are real.
#
#     @mcp.resource(
#         "epicme://entries",
#         name="entries",
#         description="All journal entries, with the URI to read each one",
#         mime_type="application/json",
#     )
#     def all_entries() -> str:
#         ...
#
# In the body: loop over `db.get_entries()` and build a lean index — one dict
# per entry with its `id`, its `title`, and a `uri` of
# f"epicme://entries/{entry.id}" so a client can follow the link straight to
# the full record. Serialize with `json.dumps(..., indent=2)`.


@mcp.resource(
    "epicme://entries/{id}",
    name="entry",
    description="A single journal entry by ID",
    mime_type="application/json",
)
def one_entry(id: str) -> str:
    entry = db.get_entry(int(id))
    if entry is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    return json.dumps(entry.to_dict(), indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
