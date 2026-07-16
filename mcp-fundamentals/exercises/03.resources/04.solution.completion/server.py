"""EpicMe MCP server — 03.resources / completion (solution)."""

import json

from mcp.server.fastmcp import FastMCP
from mcp.types import (
    Completion,
    CompletionArgument,
    CompletionContext,
    PromptReference,
    ResourceTemplateReference,
)

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


# A collection resource. Templates never appear in `resources/list`, so this
# static resource is what makes individual entries discoverable: it's the index,
# and each record carries the template URI that reads it.
@mcp.resource(
    "epicme://entries",
    name="entries",
    description="All journal entries, with the URI to read each one",
    mime_type="application/json",
)
def all_entries() -> str:
    entries = [
        {
            "id": entry.id,
            "title": entry.title,
            "uri": f"epicme://entries/{entry.id}",
        }
        for entry in db.get_entries()
    ]
    return json.dumps(entries, indent=2)


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


# One completion handler serves the whole server, so it starts by working out
# what it's being asked about and returns None for anything it doesn't handle.
@mcp.completion()
async def handle_completion(
    ref: PromptReference | ResourceTemplateReference,
    argument: CompletionArgument,
    context: CompletionContext | None,
) -> Completion | None:
    if not isinstance(ref, ResourceTemplateReference) or argument.name != "id":
        return None

    if ref.uri == "epicme://tags/{id}":
        ids = [str(tag.id) for tag in db.get_tags()]
    elif ref.uri == "epicme://entries/{id}":
        ids = [str(entry.id) for entry in db.get_entries()]
    else:
        return None

    # argument.value is what the user has typed so far — "" matches everything.
    matches = [id for id in ids if id.startswith(argument.value)]
    return Completion(values=matches, hasMore=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
