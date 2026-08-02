# Tools

A server that only answers pings is a server that can't do anything. Tools are
how you change that.

A **tool** is a function on your server that an AI model is allowed to call. You
write ordinary Python; the model reads the name, the description, and the
argument schema, decides on its own whether the function is relevant to what the
user asked, and calls it with arguments it fills in. Your code runs. The result
goes back to the model, which uses it to answer.

This is where MCP starts to differ from a typical REST or GraphQL API. In REST,
the client application usually chooses an HTTP route; in GraphQL, the client
writes a query or mutation. With an MCP tool, the model is the caller making the
choice, guided by the metadata your server publishes. The client is not merely
serializing a developer-written request: it is giving the model a bounded set
of actions and enough description to select among them.

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

## What's next?

After the three tool exercises, the course moves to **Resources**. Tools let the
model ask the server to do something; resources let the application decide which
addressable context to load, a distinction that keeps reads and actions from
collapsing into one undifferentiated API surface.
