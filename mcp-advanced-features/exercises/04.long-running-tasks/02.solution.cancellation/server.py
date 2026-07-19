"""EpicMe MCP server — long-running tasks: cancellation (solution).

A slow tool also has to handle the caller changing their mind. When a client
cancels an in-flight request, the MCP session cancels the running tool, which
surfaces inside our `await` as anyio's cancellation exception. A well-behaved
long-running tool catches that, cleans up its partial work, and lets the
cancellation propagate.

Here "cleanup" is just recording that it happened, in `LAST_CANCELLED`, so a
test can prove the cancel path ran. The render itself (`video.py`) is genuinely
cancellable; this tool passes it an `on_cancelled` hook and a `mock_seconds`
knob so a test can start a long render and cancel it mid-flight.
"""

import json
from typing import Annotated

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import CallToolResult, EmbeddedResource, ResourceLink, TextContent, TextResourceContents
from pydantic import Field

from db import DB, Entry, Tag
from video import render_wrapped_video

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


def _video_link(year: int, uri: str) -> ResourceLink:
    return ResourceLink(
        type="resource_link",
        uri=uri,
        name=f"wrapped-{year}",
        title=f"{year} Wrapped",
        description=f"Your {year} year-in-review video",
        mimeType="video/mp4",
    )


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


# --- the long-running tool -----------------------------------------------

# Set to True when a render is cancelled mid-flight, so a test (and a curious
# operator) can see the cleanup path actually ran.
LAST_CANCELLED = False


@mcp.tool()
async def create_wrapped_video(
    year: Annotated[int, Field(description="The year to summarize")],
    ctx: Context,
    mock_seconds: Annotated[float, Field(description="How long the fake render should take")] = 1.0,
) -> CallToolResult:
    """Render a wrapped video, reporting progress and cleaning up if cancelled."""
    global LAST_CANCELLED
    LAST_CANCELLED = False

    async def on_progress(fraction: float) -> None:
        await ctx.report_progress(progress=fraction, total=1.0, message="Creating video...")

    def on_cancelled() -> None:
        # The caller cancelled mid-render. A real tool would delete the partial
        # file here; we just record that cleanup ran.
        global LAST_CANCELLED
        LAST_CANCELLED = True

    uri = await render_wrapped_video(year, mock_seconds, on_progress=on_progress, on_cancelled=on_cancelled)
    return CallToolResult(content=[_text(f"Created your {year} wrapped video: {uri}"), _video_link(year, uri)])

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
