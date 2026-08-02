"""EpicMe MCP server — 04.resource-tools / linked (problem).

Your job: return links to the entries instead of the entries themselves.
Run `uv run pytest exercises/04.resource-tools/02.problem.linked` until it passes.
"""

import json
from typing import Annotated, Iterator

from mcp.server.fastmcp import FastMCP
from mcp.types import (
    CallToolResult,
    Completion,
    CompletionArgument,
    CompletionContext,
    EmbeddedResource,
    PromptReference,
    ResourceTemplateReference,
    TextContent,
    TextResourceContents,
    ResourceLink
)
from pydantic import Field

from db import DB, Entry

mcp = FastMCP(
    name="epicme",
    instructions="This lets you read and manage a personal journal.",
    port=8080
)
db = DB()
db.seed()


# --- entry results ------------------------------------------------------
#
# Both tools below answer with the same two blocks: a sentence, then the entry
# itself. Written once, so "how do we hand back an entry" has one answer.
def entry_result(entry: Entry, summary: str) -> CallToolResult:
    """A tool result carrying `summary` as text and `entry` as an embedded resource."""
    return CallToolResult(
        content=[
            TextContent(type="text", text=summary),
            EmbeddedResource(
                type="resource",
                resource=TextResourceContents(
                    # The same URI the `epicme://entries/{id}` template serves.
                    uri=f"epicme://entries/{entry.id}",
                    mimeType="application/json",
                    text=json.dumps(entry.to_dict(), indent=2),
                ),
            ),
        ]
    )


# --- tools --------------------------------------------------------------


@mcp.tool()
def create_entry(
    title: Annotated[str, Field(description="The title of the entry")],
    content: Annotated[str, Field(description="The body of the entry")],
    mood: Annotated[str | None, Field(description="The mood of the entry")] = None,
    location: Annotated[str | None, Field(description="Where it happened")] = None,
    weather: Annotated[str | None, Field(description="The weather that day")] = None,
) -> CallToolResult:
    """Create a new journal entry. Returns the created entry."""
    entry = db.create_entry(
        title=title,
        content=content,
        mood=mood,
        location=location,
        weather=weather,
    )
    return entry_result(entry, f'Entry "{entry.title}" created (id {entry.id}).')


@mcp.tool()
def get_entry(
    id: Annotated[int, Field(description="The ID of the entry to read")],
) -> CallToolResult:
    """Get a journal entry by ID. Returns the full entry."""
    entry = db.get_entry(id)
    if entry is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    return entry_result(entry, f'Entry "{entry.title}" (id {entry.id}).')


@mcp.tool()
def list_entries() -> CallToolResult:
    """List all journal entries as links. Read one with `get_entry`."""
    entries = db.get_entries()
    # TODO: add a ResourceLink to this content list for each entry.
    #
    # Resist the urge to reuse `entry_result()` here. Embedding every entry in
    # a list means the model pays for the full text of entry 47 to decide it
    # doesn't want entry 47. A link is an address it can choose to follow:
    #
    #     ResourceLink(
    #         type="resource_link",
    #         uri=...,              # where this entry lives
    #         name=...,             # a short machine-ish handle, e.g. "entry-1"
    #         title=entry.title,    # what a person actually reads
    #         description=...,      # a sentence about it
    #         mimeType="application/json",
    #     )
    #
    # Import `ResourceLink` from `mcp.types`. Build one per entry in
    # `entries`, using the same `epicme://entries/{entry.id}` URI, and unpack
    # them into the content list after the text block.
    #
    # `title` matters more than it looks: "epicme://entries/7" tells nobody
    # anything, so without it there's no way to pick the right link.

    def _gen_resource_link_for_entry(entry: Entry) -> ResourceLink | None:
        if not entry:
            return None

        return ResourceLink(
            type="resource_link",
            uri=f"epicme://entries/{entry.id}",
            name=f"entry-{entry.id}",
            title=entry.title,
            description=f"Journal entry: {entry.title}",
            mimeType="application/json"
        )

    def _gen_resource_link_for_entries() -> Iterator[ResourceLink]:
        return map(lambda entry: _gen_resource_link_for_entry(entry), entries)

    return CallToolResult(
        content=[
            TextContent(type="text", text=f"Found {len(entries)} entries."),
            *_gen_resource_link_for_entries()
        ]
    )


# --- resources ----------------------------------------------------------


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


# --- completion ---------------------------------------------------------


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

    matches = [id for id in ids if id.startswith(argument.value)]
    return Completion(values=matches, hasMore=False)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
