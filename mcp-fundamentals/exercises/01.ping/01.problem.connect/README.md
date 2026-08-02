# Connect

Your job: make `server.py` into a real MCP server that answers a ping.

## Creating the server

`FastMCP` is the server class you'll use for the whole course. It takes a name
and, optionally, instructions:

```py
mcp = FastMCP(
    name="epicme",
    instructions="This lets you solve math problems.",
)
```

The `name` is the machine-readable id other programs see. The `instructions` are
for the AI model — a sentence about what this server is *for*, so it knows when
your server is worth reaching for at all. It's easy to skip this because nothing
breaks without it. **DON'T**. It's the first thing the model learns about the mcp server.

## Running it over stdio

```py
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**stdio** means standard input and standard output. The client launches your
server as a subprocess and speaks JSON-RPC through the pipes — your server reads
requests on stdin and writes responses on stdout. It's the transport Claude
Desktop and Cursor use to run local servers, and it's why your server needs no
port, no HTTP framework, and no network access.

One consequence worth internalizing now: **stdout belongs to the protocol.** A
stray `print()` in your server writes JSON-RPC-flavored garbage into the pipe and
confuses the client. Use `print(..., file=sys.stderr)` or a logger if you want to
debug. This trips up nearly everyone once.

## Why ping is the whole exercise

A ping takes no arguments and returns nothing:

```py
result = await client.send_ping()
assert result == EmptyResult()
```

An empty response looks like a strange thing to celebrate. But getting one back
means the client launched your server, both sides completed the MCP handshake and
agreed on a protocol version, a request traveled, and a response came home. The
plumbing works. That's the foundation for every tool, resource, and prompt you'll
add for the rest of this course.

## Your task

Open `server.py` and follow the two TODOs. Then:

```sh
uv run pytest exercises/01.ping/01.problem.connect
```

Stuck? `exercises/01.ping/01.solution.connect/server.py` has the answer — diff it
against yours.

## What's next?

Next you will register the first model-controlled operation. A ping proves that
the MCP peer is alive; a tool gives the model a deliberately described action to
choose when the user's request needs it.
