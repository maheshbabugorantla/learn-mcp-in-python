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
