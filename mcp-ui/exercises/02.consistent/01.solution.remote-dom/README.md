# Remote DOM

`view_tag` now ships a remote-dom script instead of raw HTML. The new helper
builds JavaScript — inside a Python string — that creates a `ui-stack`, fills a
`ui-text` with the tag name (via `setAttribute('content', ...)`), appends it, and
hands the result to `root`:

```py
content={
    "type": "remoteDom",
    "framework": "react",
    "script": _tag_remote_dom_script(tag),
}
```

On the wire that's the same `resource` block, now with mimeType
`application/vnd.mcp-ui.remote-dom+javascript; framework=react` and your script as
`resource.text`. `_tag_html` is gone — nothing needed it once the payload changed.

The insight to carry forward: your server ships a *script*, not a picture. The
client runs that script against *its own* `ui-stack` and `ui-text` elements, so
the card comes out in the client's design system wherever it lands. You gave up
control over appearance, and consistency is what you bought with it.
