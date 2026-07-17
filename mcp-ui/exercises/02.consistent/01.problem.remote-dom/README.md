# Remote DOM

`view_tag` already returns a UI resource — a `rawHtml` one from the last topic.
Your job here is to swap the payload: build a remote-dom script and have `view_tag`
send that instead.

## Write the script builder

Above `view_tag` there's a spot for a new helper, `_tag_remote_dom_script(tag)`.
It returns a **JavaScript string** — JS source, written inside a Python string,
that the client will run later. The host hands the script a `root` node and a
document that knows the `ui-stack` and `ui-text` elements; your script assembles
them:

```py
def _tag_remote_dom_script(tag: Tag | None) -> str:
    # create a 'ui-stack' with document.createElement('ui-stack')
    # create a 'ui-text', set its text with setAttribute('content', ...)
    # append the text into the stack, then root.appendChild(stack)
    ...
```

For a missing tag, use the text `Tag not found`. And a tip worth taking:
`json.dumps(tag.name)` gives you a safely-quoted JS string literal, so a tag name
with a quote or a newline in it won't break the script you're emitting.

## Switch view_tag over

Then change the `content` you pass to `create_ui_resource` from `rawHtml` to
remote-dom:

```py
content={
    "type": "remoteDom",
    "framework": "react",
    "script": _tag_remote_dom_script(tag),
}
```

That's the one edit that changes the wire mimeType to
`application/vnd.mcp-ui.remote-dom+javascript; framework=react` and puts your
script in `resource.text`.

Once `view_tag` emits remote-dom, nothing calls `_tag_html` anymore — delete it.
(The solution does.)

```sh
uv run pytest exercises/02.consistent/01.problem.remote-dom
```

Stuck? Diff your `server.py` against the sibling
[`01.solution.remote-dom`](../01.solution.remote-dom/server.py).
