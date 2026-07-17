"""EpicMe MCP server — render-data (solution).

Most of this file is the EpicMe journal from mcp-fundamentals (tools and
resources for entries and tags). That part is background. The lesson is the
`view_*` UI tools — follow the TODOs there.
"""

import json
import os
import time
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import (
    CallToolResult,
    EmbeddedResource,
    ResourceLink,
    TextContent,
    TextResourceContents,
)
from pydantic import Field

from db import DB, Entry, Tag
from ui import create_ui_resource

# Where the iframe pages are served (the demo app under mcp-ui/demo/ serves
# them). Override with EPICME_BASE_URL if you host them elsewhere.
BASE_URL = os.environ.get("EPICME_BASE_URL", "http://localhost:8788")

mcp = FastMCP(
    name="epicme",
    instructions="This lets you read and manage a personal journal, and view it visually.",
)
db = DB()
db.seed()


def _embed(uri: str, payload: object) -> EmbeddedResource:
    return EmbeddedResource(
        type="resource",
        resource=TextResourceContents(
            uri=uri, mimeType="application/json", text=json.dumps(payload, indent=2)
        ),
    )


def entry_result(entry: Entry, summary: str) -> CallToolResult:
    return CallToolResult(
        content=[
            TextContent(type="text", text=summary),
            _embed(f"epicme://entries/{entry.id}", entry.to_dict()),
        ]
    )


# --- journal tools (background) ------------------------------------------


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
        title=title, content=content, mood=mood, location=location, weather=weather
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


# --- UI tools (the lesson) -----------------------------------------------


def _tag_remote_dom_script(tag: Tag | None) -> str:
    """A script the host runs to build a card from remote-dom elements.

    This is JavaScript in a Python string. The host hands the script a `root`
    node and a document that knows a few custom elements (ui-stack, ui-text);
    the script assembles them. Unlike raw HTML, these render in the client's own
    design system, so the card looks native wherever it lands.
    """
    if tag is not None:
        name = json.dumps(tag.name)
        description = json.dumps(tag.description or "")
        return f"""
const stack = document.createElement('ui-stack');
stack.setAttribute('direction', 'vertical');
stack.setAttribute('spacing', '20');
stack.setAttribute('align', 'center');

const title = document.createElement('ui-text');
title.setAttribute('content', {name});
stack.appendChild(title);

const description = document.createElement('ui-text');
description.setAttribute('content', {description});
stack.appendChild(description);

root.appendChild(stack);
""".strip()
    return """
const stack = document.createElement('ui-stack');
stack.setAttribute('direction', 'vertical');
stack.setAttribute('spacing', '20');
stack.setAttribute('align', 'center');

const title = document.createElement('ui-text');
title.setAttribute('content', 'Tag not found');
stack.appendChild(title);

root.appendChild(stack);
""".strip()


@mcp.tool()
def view_tag(
    id: Annotated[int, Field(description="The ID of the tag to view")],
) -> CallToolResult:
    """View a tag visually — returns a UI resource, not plain text."""
    tag = db.get_tag(id)
    return CallToolResult(
        content=[
            create_ui_resource(
                uri=f"ui://view-tag/{id}",
                content={
                    "type": "remoteDom",
                    "framework": "react",
                    "script": _tag_remote_dom_script(tag),
                },
            )
        ]
    )


@mcp.tool()
def view_journal() -> CallToolResult:
    """View the whole journal as a page loaded into an iframe."""
    iframe_url = f"{BASE_URL}/ui/journal-viewer"
    return CallToolResult(
        content=[
            create_ui_resource(
                uri=f"ui://view-journal/{int(time.time() * 1000)}",
                content={"type": "externalUrl", "iframeUrl": iframe_url},
                # A hint to the host for how big to make the frame before the
                # page has told it anything. [width, height].
                ui_metadata={"preferred-frame-size": ["600px", "800px"]},
            )
        ]
    )


@mcp.tool()
def view_entry(
    id: Annotated[int, Field(description="The ID of the entry to view")],
) -> CallToolResult:
    """View a single entry in an iframe, handed its data up front."""
    entry = db.get_entry(id)
    if entry is None:
        raise ValueError(f"Entry with ID '{id}' not found")
    # No id in the URL: the page is generic, and the entry travels in the
    # metadata as initial render data. The host gives it to the frame before
    # first paint — no round trip back to fetch what it already has.
    iframe_url = f"{BASE_URL}/ui/entry-viewer"
    return CallToolResult(
        content=[
            create_ui_resource(
                uri=f"ui://view-entry/{id}",
                content={"type": "externalUrl", "iframeUrl": iframe_url},
                ui_metadata={"initial-render-data": {"entry": entry.to_dict()}},
            )
        ]
    )


# --- resources (background) ----------------------------------------------


@mcp.resource(
    "epicme://tags",
    name="tags",
    description="All tags in the journal",
    mime_type="application/json",
)
def all_tags() -> str:
    return json.dumps([tag.to_dict() for tag in db.get_tags()], indent=2)


@mcp.resource(
    "epicme://entries",
    name="entries",
    description="All journal entries, with the URI to read each one",
    mime_type="application/json",
)
def all_entries() -> str:
    entries = [
        {"id": e.id, "title": e.title, "uri": f"epicme://entries/{e.id}"}
        for e in db.get_entries()
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


if __name__ == "__main__":
    mcp.run(transport="stdio")
