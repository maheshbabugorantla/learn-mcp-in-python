"""EpicMe MCP server — 05.prompts / optimized-prompt (problem)."""

import json
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp.types import (
    CallToolResult,
    Completion,
    CompletionArgument,
    CompletionContext,
    EmbeddedResource,
    PromptReference,
    ResourceLink,
    ResourceTemplateReference,
    TextContent,
    TextResourceContents,
)
from pydantic import Field

from db import DB, Entry

mcp = FastMCP(
    name="epicme",
    instructions="This lets you read and manage a personal journal.",
)
db = DB()
db.seed()


def _embed(uri: str, payload: object) -> EmbeddedResource:
    """Package some JSON as a resource, carrying the URI it came from.

    An EmbeddedResource travels *inside* a message or a tool result. The URI is
    the point: whoever receives it gets the data and knows what it's looking at,
    rather than a wall of anonymous JSON.
    """
    return EmbeddedResource(
        type="resource",
        resource=TextResourceContents(
            uri=uri,
            mimeType="application/json",
            text=json.dumps(payload, indent=2),
        ),
    )


def entry_result(entry: Entry, summary: str) -> CallToolResult:
    """A tool result carrying `summary` as text and `entry` as an embedded resource."""
    return CallToolResult(
        content=[
            TextContent(type="text", text=summary),
            # The same URI the `epicme://entries/{id}` template serves.
            _embed(f"epicme://entries/{entry.id}", entry.to_dict()),
        ]
    )


# --- tools: things the model decides to call -----------------------------


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
    return CallToolResult(
        content=[
            TextContent(type="text", text=f"Found {len(entries)} entries."),
            # A link is an address plus enough labelling to choose from — the
            # title is the whole point, since "epicme://entries/7" tells nobody
            # anything. The contents stay on the server until asked for.
            *(
                ResourceLink(
                    type="resource_link",
                    uri=f"epicme://entries/{entry.id}",
                    name=f"entry-{entry.id}",
                    title=entry.title,
                    description=f"Journal entry: {entry.title}",
                    mimeType="application/json",
                )
                for entry in entries
            ),
        ]
    )


@mcp.tool()
def create_tag(
    name: Annotated[str, Field(description="The name of the tag")],
    description: Annotated[str, Field(description="What the tag is for")] = "",
) -> str:
    """Create a new tag in the journal."""
    tag = db.create_tag(name, description or None)
    return f"Created tag {tag.id}: {tag.name}"


@mcp.tool()
def add_tag_to_entry(
    entry_id: Annotated[int, Field(description="The ID of the journal entry")],
    tag_id: Annotated[int, Field(description="The ID of the tag to attach")],
) -> str:
    """Attach an existing tag to an existing journal entry."""
    entry = db.get_entry(entry_id)
    if entry is None:
        raise ValueError(f"Entry with ID '{entry_id}' not found")

    tag = db.get_tag(tag_id)
    if tag is None:
        raise ValueError(f"Tag with ID '{tag_id}' not found")

    db.add_tag_to_entry(entry_id, tag_id)
    return f"Added tag '{tag.name}' to entry '{entry.title}'"


# --- resources: things the application decides to load --------------------


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


# --- prompts: things a person picks from a menu ---------------------------

# TODO: Make this prompt carry its own data.
#
# Right now it just *asks* the model to go look things up. That costs a round
# trip for the entry and another for the tags, and the model has to guess the
# right URIs to read.
#
# Instead, fetch the data here and send it along inside the messages. A
# message's `content` doesn't have to be text — an EmbeddedResource carries
# JSON plus the URI it came from, so the model gets the data and knows what
# it's looking at.
#
# You already have the helper for this: `_embed(uri, payload)` up above, the
# one your entry tools use. The same EmbeddedResource works in a prompt message
# as in a tool result — that's the nice part.
#
# Look the entry up with `db.get_entry(int(entry_id))` and the tags with
# `db.get_tags()`. Then change the return type to `list[base.Message]` and
# return three messages:
#   1. base.UserMessage("...instructions...")
#   2. base.UserMessage(_embed(f"epicme://entries/{entry.id}", entry.to_dict()))
#   3. base.UserMessage(_embed("epicme://tags", tags))
#
# Raise a ValueError if the entry doesn't exist — the prompt does the fetching
# now, so it can fail in a way it couldn't before.
@mcp.prompt(
    name="suggest_tags",
    description="Suggest tags for a journal entry",
)
def suggest_tags(
    entry_id: Annotated[
        str, Field(description="The ID of the journal entry to suggest tags for")
    ],
) -> str:
    return (
        f"Look up the journal entry with ID {entry_id} and read it. "
        f"Then look at the tags that already exist in the journal. "
        f"Suggest which of those tags fit this entry, and suggest any new tags "
        f"worth creating. Explain your reasoning briefly, and ask me to approve "
        f"before changing anything."
    )


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
    mcp.run(transport="stdio")
