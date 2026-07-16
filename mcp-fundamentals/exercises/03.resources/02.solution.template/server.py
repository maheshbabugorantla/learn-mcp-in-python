"""EpicMe MCP server — 03.resources / template (solution)."""

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
