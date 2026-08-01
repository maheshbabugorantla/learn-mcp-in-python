"""EpicMe MCP server — 03.resources / simple (problem).

Your job: expose the journal's tags as a resource at `epicme://tags`.
Run `uv run pytest exercises/03.resources/01.problem.simple` until it passes.
"""

import json

from mcp.server.fastmcp import FastMCP

from db import DB

mcp = FastMCP(
    name="epicme",
    instructions="This lets you read and manage a personal journal.",
    port=8080,
)
db = DB()
db.seed()


# The decorator carries the URI; the function returns the contents as a string.
# Describe it properly — `description` is what a user sees in a picker UI, and
# `mime_type` is how the client knows to treat your output as JSON, not prose.
#
#     @mcp.resource(
#         "epicme://tags",
#         name="tags",
#         description="All tags in the journal",
#         mime_type="application/json",
#     )
#     def all_tags() -> str:
#         ...
#
# In the body: get every tag with `db.get_tags()`, turn each one into a plain
# dict with its `.to_dict()` helper, and serialize the list with
# `json.dumps(..., indent=2)`.


@mcp.resource(
    "epicme://tags",
    name="tags",
    description="All tags in the journal",
    mime_type="application/json"
)
def all_tags() -> str:
    tags = db.get_tags()
    return json.dumps(list(map(lambda tag: tag.to_dict(), tags)), indent=2)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
