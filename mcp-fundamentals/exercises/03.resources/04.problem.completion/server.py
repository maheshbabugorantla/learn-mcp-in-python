"""EpicMe MCP server — 03.resources / completion (problem).

Your job: suggest valid ids for the `{id}` in your resource templates.
Run `uv run pytest exercises/03.resources/04.problem.completion` until it passes.
"""

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


# TODO: Register a completion handler with `@mcp.completion()`.
#
# This is ONE handler for the whole server — every template and prompt argument
# arrives here — so it has to work out what it's being asked and return None for
# anything it doesn't handle. (The imports above are the pieces you'll need.)
#
#     @mcp.completion()
#     async def handle_completion(
#         ref: PromptReference | ResourceTemplateReference,
#         argument: CompletionArgument,
#         context: CompletionContext | None,
#     ) -> Completion | None:
#         ...
#
# In the body:
#   1. Bail out with `return None` unless this is a ResourceTemplateReference
#      and `argument.name == "id"`.
#   2. Dispatch on `ref.uri` — the raw pattern string, "epicme://tags/{id}" or
#      "epicme://entries/{id}" — to pick `db.get_tags()` or `db.get_entries()`.
#      Ids are ints in the DB and strings on the wire, so `str(tag.id)`.
#   3. Filter by what the user has typed so far:
#      `[id for id in ids if id.startswith(argument.value)]`
#   4. Return `Completion(values=matches, hasMore=False)`.


if __name__ == "__main__":
    mcp.run(transport="stdio")
