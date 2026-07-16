"""The EpicMe MCP server — the journal, before it knows who's reading it.

Every tool here serves the same person's journal, because nothing has told it
otherwise yet. `04.user` is where that changes.
"""

from __future__ import annotations

import json
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import (
    CallToolResult,
    EmbeddedResource,
    ResourceLink,
    TextContent,
    TextResourceContents,
)
from pydantic import Field

from epicme.db import DB, Entry
from epicme.provider import DEFAULT_USER_ID, USERS

db = DB()
for user_id in USERS:
    db.seed(user_id)

mcp = FastMCP(
    name="epicme",
    instructions="This lets you read and manage your personal journal.",
    # Each request is handled on its own, in the task that received it, with
    # no session carried between them. This setting matters more than it
    # looks — `04.user` is where you find out why.
    stateless_http=True,
    json_response=True,
    # Serve the MCP endpoint at the root of *this* app, so `app.py` can mount
    # the whole thing at `/mcp` and guard exactly that path and nothing else.
    streamable_http_path="/",
    # We're behind our own Starlette app, so let it decide what hosts are
    # allowed rather than having the SDK second-guess it.
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


def _embed(uri: str, payload: object) -> EmbeddedResource:
    """Package some JSON as a resource, carrying the URI it came from."""
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
            _embed(f"epicme://entries/{entry.id}", entry.to_dict()),
        ]
    )


# --- tools ----------------------------------------------------------------


@mcp.tool()
def create_entry(
    title: Annotated[str, Field(description="The title of the entry")],
    content: Annotated[str, Field(description="The body of the entry")],
    mood: Annotated[str | None, Field(description="The mood of the entry")] = None,
    location: Annotated[str | None, Field(description="Where it happened")] = None,
    weather: Annotated[str | None, Field(description="The weather that day")] = None,
) -> CallToolResult:
    """Create a new journal entry. Returns the created entry."""
    # Whoever is calling, they get Kody's journal. That's the placeholder
    # `04.user` replaces with the actual authenticated user.
    user_id = DEFAULT_USER_ID
    entry = db.create_entry(
        user_id,
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
    """Get one of your journal entries by ID. Returns the full entry."""
    # Whoever is calling, they get Kody's journal. That's the placeholder
    # `04.user` replaces with the actual authenticated user.
    user_id = DEFAULT_USER_ID
    entry = db.get_entry(user_id, id)
    if entry is None:
        # Someone else's entry and an entry that doesn't exist give the same
        # answer on purpose. "Not yours" and "not there" are the same fact as
        # far as this caller is entitled to know.
        raise ValueError(f"Entry with ID '{id}' not found")
    return entry_result(entry, f'Entry "{entry.title}" (id {entry.id}).')


@mcp.tool()
def list_entries() -> CallToolResult:
    """List your journal entries as links. Read one with `get_entry`."""
    # Whoever is calling, they get Kody's journal. That's the placeholder
    # `04.user` replaces with the actual authenticated user.
    user_id = DEFAULT_USER_ID
    entries = db.get_entries(user_id)
    return CallToolResult(
        content=[
            TextContent(type="text", text=f"Found {len(entries)} entries."),
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
    """Create a new tag in your journal."""
    # Whoever is calling, they get Kody's journal. That's the placeholder
    # `04.user` replaces with the actual authenticated user.
    user_id = DEFAULT_USER_ID
    tag = db.create_tag(user_id, name, description or None)
    return f"Created tag {tag.id}: {tag.name}"


@mcp.tool()
def add_tag_to_entry(
    entry_id: Annotated[int, Field(description="The ID of the journal entry")],
    tag_id: Annotated[int, Field(description="The ID of the tag to attach")],
) -> str:
    """Attach one of your tags to one of your journal entries."""
    # Whoever is calling, they get Kody's journal. That's the placeholder
    # `04.user` replaces with the actual authenticated user.
    user_id = DEFAULT_USER_ID
    entry = db.get_entry(user_id, entry_id)
    if entry is None:
        raise ValueError(f"Entry with ID '{entry_id}' not found")

    tag = db.get_tag(user_id, tag_id)
    if tag is None:
        raise ValueError(f"Tag with ID '{tag_id}' not found")

    db.add_tag_to_entry(user_id, entry_id, tag_id)
    return f"Added tag '{tag.name}' to entry '{entry.title}'"


# --- resources ------------------------------------------------------------


@mcp.resource(
    "epicme://tags",
    name="tags",
    description="All of your tags",
    mime_type="application/json",
)


def all_tags() -> str:
    # Whoever is calling, they get Kody's journal. That's the placeholder
    # `04.user` replaces with the actual authenticated user.
    user_id = DEFAULT_USER_ID
    return json.dumps(
        [tag.to_dict() for tag in db.get_tags(user_id)], indent=2
    )


@mcp.resource(
    "epicme://entries",
    name="entries",
    description="All of your journal entries, with the URI to read each one",
    mime_type="application/json",
)


def all_entries() -> str:
    # Whoever is calling, they get Kody's journal. That's the placeholder
    # `04.user` replaces with the actual authenticated user.
    user_id = DEFAULT_USER_ID
    return json.dumps(
        [
            {
                "id": entry.id,
                "title": entry.title,
                "uri": f"epicme://entries/{entry.id}",
            }
            for entry in db.get_entries(user_id)
        ],
        indent=2,
    )


@mcp.resource(
    "epicme://entries/{id}",
    name="entry",
    description="One of your journal entries by ID",
    mime_type="application/json",
)


def one_entry(id: str) -> str:
    # Whoever is calling, they get Kody's journal. That's the placeholder
    # `04.user` replaces with the actual authenticated user.
    user_id = DEFAULT_USER_ID
    entry = db.get_entry(user_id, int(id))
    if entry is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    return json.dumps(entry.to_dict(), indent=2)


# --- prompts --------------------------------------------------------------


@mcp.prompt(
    name="suggest_tags",
    description="Suggest tags for one of your journal entries",
)


def suggest_tags(
    entry_id: Annotated[
        str, Field(description="The ID of the journal entry to suggest tags for")
    ],
) -> list[base.Message]:
    # A prompt is a person picking from a menu, but it still runs on the server
    # with somebody's token — so it asks the same question every tool asks.
    # Whoever is calling, they get Kody's journal. That's the placeholder
    # `04.user` replaces with the actual authenticated user.
    user_id = DEFAULT_USER_ID

    entry = db.get_entry(user_id, int(entry_id))
    if entry is None:
        raise ValueError(f"Entry with ID '{entry_id}' not found")
    tags = [tag.to_dict() for tag in db.get_tags(user_id)]

    return [
        base.UserMessage(
            "Read this journal entry and the tags that already exist. Suggest which "
            "existing tags fit, and any new tags worth creating. You can create tags "
            "with `create_tag` and attach them with `add_tag_to_entry`. Explain your "
            "reasoning briefly, and ask me to approve before changing anything."
        ),
        base.UserMessage(_embed(f"epicme://entries/{entry.id}", entry.to_dict())),
        base.UserMessage(_embed("epicme://tags", tags)),
    ]
