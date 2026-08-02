# Ping

Before a server can be useful, it has to exist and it has to be reachable. That's
this topic — the smallest possible MCP server, and proof that something on the
other end is listening.

MCP (the Model Context Protocol) is a standard way for a program like Claude
Desktop, Cursor, or ChatGPT to talk to code you wrote. You run a **server**; the
AI app is a **client**. The protocol defines how they introduce themselves and
what they're allowed to ask each other for.

The value is in that standardization. You don't write a Claude integration and
then a Cursor integration. You write one MCP server, and every client that speaks
the protocol can use it.

If you know REST, think of this as the moment before you add `GET` and `POST`
routes: first establish a durable protocol peer. If you know GraphQL, this is
before the schema is useful: the client and server still need a negotiated
connection over which discovery and requests can happen. MCP clients commonly
launch local servers as long-lived subprocesses, so the connection itself is
part of the product, not just setup around an endpoint.

One step:

1. **connect** — create a server, run it over stdio, and answer a ping.

A ping is deliberately the most boring request in the protocol. It takes no
arguments and returns nothing. That's exactly why it's a good first target: if a
ping comes back, the transport works, the handshake completed, and both sides
agree they're speaking MCP. Everything else in this course is built on that.

Run the exercise's tests from the repo root, one directory at a time:

```sh
uv run pytest exercises/01.ping/01.problem.connect
```

## What’s next?

Next, the server will become useful: **Tools** adds operations the model can
choose to call. That is the first important MCP control boundary — the model
does not invent arbitrary Python calls; it chooses from the tools your server
advertises.
