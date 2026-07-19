"""EpicMe MCP server — sampling (advanced, problem).

The simple step used sampling for a throwaway reflection. Here you make it earn
its keep: after creating an entry, ask the client's LLM to suggest 1-3 tag names
for it, then actually create and attach those tags. The model's text drives a
real database change — that's the payoff of sampling.

Two wrinkles your code has to handle: the model returns free text, so parse the
comma-separated list yourself; and a suggested tag may already exist (the schema
makes tag names unique), so find-or-create by name rather than blindly insert
(that helper is written for you). `create_entry` is the lesson; everything else
is the base journal.
"""

import json
from typing import Annotated

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import CallToolResult, ResourceLink, SamplingMessage, TextContent
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


async def _suggest_tags(ctx: Context, entry: Entry) -> list[str]:
    """Ask the client's LLM for 1-3 tag names for the entry, parsed to a list.

    Returns an empty list if the client can't sample (no sampling capability
    means create_message errors), so the entry is still created either way.
    """
    try:
        # 🐨 ask the client's model for tag names for this entry:
        #    res = await ctx.session.create_message(
        #        messages=[
        #            SamplingMessage(
        #                role="user",
        #                content=TextContent(
        #                    type="text",
        #                    text=f'Suggest 1 to 3 short tag names for this journal entry. '
        #                    f'Title: "{entry.title}". Content: {entry.content}',
        #                ),
        #            )
        #        ],
        #        max_tokens=100,
        #        system_prompt="You label journal entries. Reply with ONLY 1-3 comma-separated, "
        #        "lowercase tag names and nothing else.",
        #    )
        # 🐨 parse the model's comma-separated text into a list of names:
        #    text = getattr(res.content, "text", "") or ""
        #    return [name.strip() for name in text.split(",") if name.strip()]
        # 💣 delete this once you do (the tag test drives it):
        raise NotImplementedError("Ask the model for tag names with ctx.session.create_message (see the TODO).")
    except Exception:
        return []


def _find_or_create_tag(name: str) -> Tag:
    """Return the existing tag with this name, or create one. Names are unique."""
    for tag in db.get_tags():
        if tag.name == name:
            return tag
    return db.create_tag(name)


# --- entry tools ---------------------------------------------------------


@mcp.tool()
async def create_entry(
    title: Annotated[str, Field(description="The title of the entry")],
    content: Annotated[str, Field(description="The body of the entry")],
    ctx: Context,
    mood: Annotated[str | None, Field(description="The mood of the entry")] = None,
) -> CallToolResult:
    """Create a new journal entry, auto-tagged by the client's LLM when available."""
    entry = db.create_entry(title=title, content=content, mood=mood)
    result = CallToolResult(content=[_text(f'Created entry "{entry.title}" (id {entry.id}).'), _entry_link(entry)])
    added: list[str] = []
    for name in await _suggest_tags(ctx, entry):
        tag = _find_or_create_tag(name)
        db.add_tag_to_entry(entry.id, tag.id)
        added.append(tag.name)
    if added:
        result.content.append(_text(f"Added tags: {', '.join(added)}"))
    return result


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
