# A one-line reflection

One `create_message` inside `_reflect`, and `create_entry` now speaks to the
model as easily as it speaks to the database. You send a prompt plus a
`system_prompt` to shape the tone, and read the reply off `res.content.text`.

The two guardrails matter as much as the call. `getattr(res.content, "text", None)`
means a surprising reply shape returns `None` rather than crashing, and the
`try/except` around `_reflect` in `create_entry` means a client that can't sample
still gets its entry saved. The fake-model test proves the reflection lands; the
no-sampling test proves the tool survives without one.

That's the whole shape of sampling: the server asked, the model answered, and the
tool folded the answer into its result — all without the caller doing a thing.
