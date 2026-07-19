"""EpicMe MCP server — tool annotations (problem).

The base journal has a dozen tools and, to a client, they all look alike — a
name, a description, a schema. But some only read, some quietly overwrite, and
two delete for good. Annotations are the metadata that tells a client which is
which: a read-only tool can be called freely, a destructive one deserves a
confirmation, an idempotent one is safe to retry.

Right now every tool is un-annotated. Your job is to add a `ToolAnnotations`
to each one so a client can tell them apart.
"""

import json
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, ResourceLink, TextContent
from pydantic import Field

from db import DB, Entry, Tag

mcp = FastMCP(name="epicme", instructions="Read and manage a personal journal.")
db = DB()
db.seed()


def _text(value: object) -> TextContent:
    text = value if isinstance(value, str) else json.dumps(value)
    return TextContent(type="text", text=text)


def _entry_link(entry: Entry) -> ResourceLink:
    return ResourceLink(
        type="resource_link",
        uri=f"epicme://entries/{entry.id}",
        name=f"entry-{entry.id}",
        title=entry.title,
        description=f"Journal entry: {entry.title}",
        mimeType="application/json",
    )


def _tag_link(tag: Tag) -> ResourceLink:
    return ResourceLink(
        type="resource_link",
        uri=f"epicme://tags/{tag.id}",
        name=f"tag-{tag.id}",
        title=tag.name,
        description=f"Tag: {tag.name}",
        mimeType="application/json",
    )


# 🐨 Annotate every tool below with a `ToolAnnotations`.
#    First import it: `from mcp.types import ToolAnnotations`.
#    Then pass it to each decorator, e.g. `@mcp.tool(annotations=ToolAnnotations(...))`.
#    The fields are advisory hints; set them by what the tool actually does:
#      • read tools  (get_entry, get_tag, list_entries, list_tags)
#          → readOnlyHint=True, openWorldHint=False, plus a human `title`
#      • delete tools (delete_entry, delete_tag)
#          → destructiveHint=True, idempotentHint=True
#      • update tools (update_entry, update_tag)
#          → idempotentHint=True, destructiveHint=False
#      • create/attach tools (create_entry, create_tag, add_tag_to_entry)
#          → destructiveHint=False, plus a `title`
# 💣 The tools work fine as-is, but the tests read these hints back through
#    `list_tools()` and will fail until the annotations are in place.


# --- entry tools ---------------------------------------------------------


@mcp.tool()
def create_entry(
    title: Annotated[str, Field(description="The title of the entry")],
    content: Annotated[str, Field(description="The body of the entry")],
    mood: Annotated[str | None, Field(description="The mood of the entry")] = None,
) -> CallToolResult:
    """Create a new journal entry."""
    entry = db.create_entry(title=title, content=content, mood=mood)
    return CallToolResult(content=[_text(f'Created entry "{entry.title}" (id {entry.id}).'), _entry_link(entry)])


@mcp.tool()
def get_entry(id: Annotated[int, Field(description="The entry ID")]) -> CallToolResult:
    """Get a journal entry by ID."""
    entry = db.get_entry(id)
    if entry is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    return CallToolResult(content=[_text(entry.to_dict()), _entry_link(entry)])


@mcp.tool()
def list_entries() -> CallToolResult:
    """List all journal entries."""
    entries = db.get_entries()
    return CallToolResult(content=[_text(f"Found {len(entries)} entries."), *(_entry_link(e) for e in entries)])


@mcp.tool()
def update_entry(
    id: Annotated[int, Field(description="The entry ID")],
    title: Annotated[str | None, Field(description="A new title")] = None,
    content: Annotated[str | None, Field(description="New body text")] = None,
    mood: Annotated[str | None, Field(description="A new mood")] = None,
) -> CallToolResult:
    """Update a journal entry. Only provided fields change."""
    if db.get_entry(id) is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    fields = {k: v for k, v in (("title", title), ("content", content), ("mood", mood)) if v is not None}
    entry = db.update_entry(id, **fields)
    return CallToolResult(content=[_text(f'Updated entry "{entry.title}" (id {entry.id}).'), _entry_link(entry)])


@mcp.tool()
def delete_entry(id: Annotated[int, Field(description="The entry ID")]) -> CallToolResult:
    """Delete a journal entry."""
    entry = db.get_entry(id)
    if entry is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    db.delete_entry(id)
    return CallToolResult(content=[_text(f'Deleted entry "{entry.title}" (id {id}).')])


# --- tag tools -----------------------------------------------------------


@mcp.tool()
def create_tag(
    name: Annotated[str, Field(description="The tag name")],
    description: Annotated[str, Field(description="What the tag is for")] = "",
) -> CallToolResult:
    """Create a new tag."""
    tag = db.create_tag(name, description or None)
    return CallToolResult(content=[_text(f'Created tag "{tag.name}" (id {tag.id}).'), _tag_link(tag)])


@mcp.tool()
def get_tag(id: Annotated[int, Field(description="The tag ID")]) -> CallToolResult:
    """Get a tag by ID."""
    tag = db.get_tag(id)
    if tag is None:
        raise ValueError(f"Tag with ID '{id}' not found")
    return CallToolResult(content=[_text(tag.to_dict()), _tag_link(tag)])


@mcp.tool()
def list_tags() -> CallToolResult:
    """List all tags."""
    tags = db.get_tags()
    return CallToolResult(content=[_text(f"Found {len(tags)} tags."), *(_tag_link(t) for t in tags)])


@mcp.tool()
def update_tag(
    id: Annotated[int, Field(description="The tag ID")],
    name: Annotated[str | None, Field(description="A new name")] = None,
    description: Annotated[str | None, Field(description="A new description")] = None,
) -> CallToolResult:
    """Update a tag. Only provided fields change."""
    if db.get_tag(id) is None:
        raise ValueError(f"Tag with ID '{id}' not found")
    fields = {k: v for k, v in (("name", name), ("description", description)) if v is not None}
    tag = db.update_tag(id, **fields)
    return CallToolResult(content=[_text(f'Updated tag "{tag.name}" (id {tag.id}).'), _tag_link(tag)])


@mcp.tool()
def delete_tag(id: Annotated[int, Field(description="The tag ID")]) -> CallToolResult:
    """Delete a tag."""
    tag = db.get_tag(id)
    if tag is None:
        raise ValueError(f"Tag with ID '{id}' not found")
    db.delete_tag(id)
    return CallToolResult(content=[_text(f'Deleted tag "{tag.name}" (id {id}).')])


@mcp.tool()
def add_tag_to_entry(
    entry_id: Annotated[int, Field(description="The entry ID")],
    tag_id: Annotated[int, Field(description="The tag ID")],
) -> CallToolResult:
    """Attach a tag to an entry."""
    entry = db.get_entry(entry_id)
    if entry is None:
        raise ValueError(f"Entry with ID '{entry_id}' not found")
    tag = db.get_tag(tag_id)
    if tag is None:
        raise ValueError(f"Tag with ID '{tag_id}' not found")
    db.add_tag_to_entry(entry_id, tag_id)
    return CallToolResult(content=[_text(f'Added tag "{tag.name}" to entry "{entry.title}".')])


# --- resources -----------------------------------------------------------


@mcp.resource("epicme://tags", name="tags", description="All tags", mime_type="application/json")
def all_tags() -> str:
    return json.dumps([t.to_dict() for t in db.get_tags()], indent=2)


@mcp.resource("epicme://tags/{id}", name="tag", description="A tag by ID", mime_type="application/json")
def one_tag(id: str) -> str:
    tag = db.get_tag(int(id))
    if tag is None:
        raise ValueError(f"Tag with ID '{id}' not found")
    return json.dumps(tag.to_dict(), indent=2)


@mcp.resource("epicme://entries", name="entries", description="All entries", mime_type="application/json")
def all_entries() -> str:
    return json.dumps([{"id": e.id, "title": e.title, "uri": f"epicme://entries/{e.id}"} for e in db.get_entries()], indent=2)


@mcp.resource("epicme://entries/{id}", name="entry", description="An entry by ID", mime_type="application/json")
def one_entry(id: str) -> str:
    entry = db.get_entry(int(id))
    if entry is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    return json.dumps(entry.to_dict(), indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
