# Tools

A server that only answers pings is a server that can't do anything. Tools are
how you change that.

A **tool** is a function on your server that an AI model is allowed to call. You
write ordinary Python; the model reads the name, the description, and the
argument schema, decides on its own whether the function is relevant to what the
user asked, and calls it with arguments it fills in. Your code runs. The result
goes back to the model, which uses it to answer.

That's the whole loop, and it's worth sitting with how unusual it is. You are not
writing an API for another programmer who will read your docs and get the call
right. You are writing an API for a reader who only ever sees what you chose to
put in the schema, and who is guessing. Everything in this topic is about making
that guess easy.

Three steps:

1. **simple** — register your first tool with `@mcp.tool()` and watch it show up
   over the wire.
2. **args** — give the tool arguments, and learn how Python's type hints turn
   into the JSON Schema the model reads. Then make each argument describe itself.
3. **errors** — let a tool fail on purpose, and see why a raised exception is a
   message to the model rather than a crash.

Run each exercise's tests from the repo root, one directory at a time:

```sh
uv run pytest exercises/02.tools/01.problem.simple
```
