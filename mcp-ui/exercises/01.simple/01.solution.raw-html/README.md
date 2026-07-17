# Raw HTML

`view_tag` now returns a UI resource instead of giving up:

```py
tag = db.get_tag(id)
return CallToolResult(
    content=[
        create_ui_resource(
            uri=f"ui://view-tag/{id}",
            content={"type": "rawHtml", "htmlString": _tag_html(tag, id)},
        )
    ]
)
```

On the wire that's a `resource` block whose `resource.mimeType` is `text/html`
and whose `resource.text` is your HTML string. A UI-aware client sees the block,
reads the mimeType, and renders the HTML.

Raw HTML is the simplest UI resource there is — you write the markup, you ship it,
the client draws it. The catch is right there in "draws it": it renders your
markup *as-is*, so your card looks like your card no matter whose client it lands
in. In a polished app with its own design system, that reads as foreign. Topic 02
fixes exactly that.
