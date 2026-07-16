"""EpicMe MCP server — 03.resources / template (problem).

Your job: serve individual tags and entries through resource templates.
Run `uv run pytest exercises/03.resources/02.problem.template` until it passes.
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


# TODO: Register a resource template at `epicme://tags/{id}`.
#
# The `{id}` placeholder MUST match the function's parameter name exactly, or
# FastMCP raises at import time and the server never starts.
#
#     @mcp.resource(
#         "epicme://tags/{id}",
#         name="tag",
#         description="A single tag by ID",
#         mime_type="application/json",
#     )
#     def one_tag(id: str) -> str:
#         ...
#
# In the body: `id` arrives as a string (it came out of a URI), so cast it —
# `db.get_tag(int(id))`. That returns None when there's no such tag, so raise
# a ValueError mentioning the id. FastMCP turns the exception into a proper
# MCP error for the client.


# TODO: Register a second template at `epicme://entries/{id}`.
#
# Same shape, but use `db.get_entry(int(id))`. An entry's `.to_dict()` already
# includes its tags, so there's nothing extra to join.


if __name__ == "__main__":
    mcp.run(transport="stdio")
