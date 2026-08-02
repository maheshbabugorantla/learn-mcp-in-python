"""EpicMe MCP server — 04.resource-tools / embedded (problem).

Your job: hand the whole entry back from a tool, not just a sentence about it.
Run `uv run pytest exercises/04.resource-tools/01.problem.embedded` until it passes.
"""

import json
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import (
    CallToolResult,
    Completion,
    CompletionArgument,
    CompletionContext,
    PromptReference,
    ResourceTemplateReference,
    TextContent,
    EmbeddedResource,
    TextResourceContents,
)
from pydantic import Field

from db import DB, Entry

mcp = FastMCP(
    name="epicme",
    instructions="This lets you read and manage a personal journal.",
    port=8080,
)

db = DB()
db.seed()


# --- entry results ------------------------------------------------------
#
# Both tools below answer with an entry, so they both come through here. Fix
# this one function and both tools are fixed.
def entry_result(entry: Entry, summary: str) -> CallToolResult:
    """A tool result carrying `summary` as text and `entry` as an embedded resource."""
    # Right now the model gets a sentence and nothing else — it would have to
    # turn around and call `resources/read` to see what was actually saved.
    # Put the record inline instead, as a second block after the text:
    #
    #     EmbeddedResource(
    #         type="resource",
    #         resource=TextResourceContents(
    #             uri=...,          # the URI this entry lives at
    #             mimeType="application/json",
    #             text=...,         # the entry, serialized
    #         ),
    #     )
    #
    # Import `EmbeddedResource` and `TextResourceContents` from `mcp.types`.
    # For the `uri`, use the same address the `epicme://entries/{id}` template
    # serves: f"epicme://entries/{entry.id}". For the `text`, serialize the
    # record with `json.dumps(entry.to_dict(), indent=2)`.
    #
    # Keep the text block first: it's what a human skimming the transcript
    # reads. The resource is the payload underneath it.
    embedded_resource = EmbeddedResource(
        type="resource",
        resource=TextResourceContents(
            uri=f"epicme://entries/{entry.id}",
            mimeType="application/json",
            text=json.dumps(entry.to_dict(), indent=2),
        )
    )
    return CallToolResult(
        content=[
            TextContent(type="text", text=summary),
            embedded_resource,
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
