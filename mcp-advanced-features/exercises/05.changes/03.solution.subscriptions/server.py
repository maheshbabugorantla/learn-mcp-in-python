"""EpicMe MCP server — resource subscriptions (solution).

`resources/list_changed` says "the *collection* changed." Subscriptions are
finer-grained: a client can say "I care about this *one* resource — tell me when
*it* changes" and the server answers each edit with
`notifications/resources/updated` for that exact URI.

FastMCP (1.28) doesn't wrap subscriptions, so there are no `@mcp.subscribe`
decorators to reach for. The subscribe/unsubscribe handlers live on the
low-level `Server` that FastMCP is built on, which we get at via
`mcp._mcp_server`. That's not a blessed public API — it's the real answer for
this feature in this version, and worth knowing it's what FastMCP delegates to
underneath. We keep a module-level set of the subscribed URI strings, and when
`update_entry` or `delete_entry` touches a subscribed entry we notify with
`ctx.session.send_resource_updated(...)`.
"""

import json
from typing import Annotated

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import CallToolResult, ResourceLink, TextContent
from pydantic import AnyUrl, Field

from db import DB, Entry, Tag

mcp = FastMCP(name="epicme", instructions="Read and manage a personal journal.")
db = DB()
db.seed()


# --- the lesson: resource subscriptions ----------------------------------
#
# Which resource URIs a client has asked to watch. FastMCP has no public hook
# for this, so we register the subscribe/unsubscribe handlers directly on the
# low-level server FastMCP wraps.
_subscribed: set[str] = set()


@mcp._mcp_server.subscribe_resource()
async def _subscribe(uri: AnyUrl) -> None:
    _subscribed.add(str(uri))


@mcp._mcp_server.unsubscribe_resource()
async def _unsubscribe(uri: AnyUrl) -> None:
    _subscribed.discard(str(uri))


async def _notify_entry_changed(ctx: Context, entry_id: int) -> None:
    """If a client is watching this entry, tell it the entry changed."""
    uri = f"epicme://entries/{entry_id}"
    if uri in _subscribed:
        await ctx.session.send_resource_updated(uri=AnyUrl(uri))


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


# --- the lesson: a tool that adds another tool ---------------------------


def beta_ping() -> CallToolResult:
    """A beta tool that only exists once beta tools are enabled."""
    return CallToolResult(content=[_text("pong")])


@mcp.tool()
async def enable_beta_tools(ctx: Context) -> CallToolResult:
    """Register the beta toolset and tell the client the tool list changed.

    Registering `beta_ping` makes it callable, but a client that already fetched
    the tool list won't know it's there. `send_tool_list_changed()` is the nudge
    that tells the client to call `tools/list` again.
    """
    mcp.add_tool(beta_ping, name="beta_ping", description="A beta tool. Returns pong.")
    await ctx.session.send_tool_list_changed()
    return CallToolResult(content=[_text("Beta tools enabled. `beta_ping` is now available.")])


# --- entry tools ---------------------------------------------------------


@mcp.tool()
async def create_entry(
    title: Annotated[str, Field(description="The title of the entry")],
    content: Annotated[str, Field(description="The body of the entry")],
    ctx: Context,
    mood: Annotated[str | None, Field(description="The mood of the entry")] = None,
) -> CallToolResult:
    """Create a new journal entry."""
    entry = db.create_entry(title=title, content=content, mood=mood)
    # The epicme://entries collection just gained a row — tell the client.
    await ctx.session.send_resource_list_changed()
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
async def update_entry(
    id: Annotated[int, Field(description="The entry ID")],
    ctx: Context,
    title: Annotated[str | None, Field(description="A new title")] = None,
    content: Annotated[str | None, Field(description="New body text")] = None,
    mood: Annotated[str | None, Field(description="A new mood")] = None,
) -> CallToolResult:
    """Update a journal entry. Only provided fields change."""
    if db.get_entry(id) is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    fields = {k: v for k, v in (("title", title), ("content", content), ("mood", mood)) if v is not None}
    entry = db.update_entry(id, **fields)
    # If someone subscribed to epicme://entries/{id}, this edit is what they
    # asked to hear about.
    await _notify_entry_changed(ctx, id)
    return CallToolResult(content=[_text(f'Updated entry "{entry.title}" (id {entry.id}).'), _entry_link(entry)])


@mcp.tool()
async def delete_entry(
    id: Annotated[int, Field(description="The entry ID")], ctx: Context
) -> CallToolResult:
    """Delete a journal entry."""
    entry = db.get_entry(id)
    if entry is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    db.delete_entry(id)
    # A subscriber to this entry should hear that it's gone (their next fetch 404s).
    await _notify_entry_changed(ctx, id)
    return CallToolResult(content=[_text(f'Deleted entry "{entry.title}" (id {id}).')])


# --- tag tools -----------------------------------------------------------


@mcp.tool()
async def create_tag(
    name: Annotated[str, Field(description="The tag name")],
    ctx: Context,
    description: Annotated[str, Field(description="What the tag is for")] = "",
) -> CallToolResult:
    """Create a new tag."""
    tag = db.create_tag(name, description or None)
    # The epicme://tags collection just gained a row — tell the client.
    await ctx.session.send_resource_list_changed()
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
