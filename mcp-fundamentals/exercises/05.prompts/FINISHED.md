# You're done

You started with a server that could answer a ping and nothing else. You now have
an MCP server with all three primitives, and — more to the point — you know which
one to reach for.

Here's what you built:

- **A server that connects** over stdio, the transport real clients use to launch
  local servers.
- **Tools** the model can call, with schemas generated from your type hints and
  errors that come back as messages it can recover from.
- **Resources** the application can load: static ones, URI templates for
  individual records, and collections that make records discoverable.
- **Tools that return resources** — embedded when the model needs the data now,
  linked when the list could be long and the client should fetch only what it
  opens.
- **Prompts** a person picks from a menu, carrying their own context, with
  argument completion so nobody has to memorize an id.

The thread running through all of it: **the other end is guessing.** Every
description, every schema, every URI is context for a reader who can't see your
code. That instinct is most of what makes an MCP server good, and it's the part
that transfers to whatever you build next.

## Where to go next

**Run it against a real client.** This is the fun part, and everything so far has
been building to it. Your finished server is
`exercises/05.prompts/03.solution.completion/server.py`. Point Claude Desktop or
Cursor at it via stdio — in Claude Desktop that's `claude_desktop_config.json`,
with the command that runs your server. Then ask it about your journal and watch
the tools you wrote get called by a model you didn't configure.

**Poke at it with the Inspector.** A browser UI for calling tools, reading
resources, and rendering prompts by hand:

```sh
cd exercises/05.prompts/03.solution.completion
uv run mcp dev server.py
```

(This one shells out to `npx`, so it needs Node — the only place in this course
that does.)

**Build your own.** The obvious next move is to point a server at something you
actually use. The shape you learned here — a `db`, some tools, some resources,
a prompt — is most of what a real server looks like.

**Read the spec.** [modelcontextprotocol.io](https://modelcontextprotocol.io) is
readable and short. It also covers ground this course didn't: sampling (your
server asking the *model* for a completion), roots, notifications, and
streamable HTTP for servers that don't run as a local subprocess.

**Read the SDK.** [`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk)
has an `examples/` directory worth skimming. One heads-up: this course pins
`mcp==1.28.1`, and a v2 is in beta that renames `FastMCP` to `MCPServer` and
moves the types to a separate `mcp_types` package. The concepts you learned all
carry over — the imports move. The SDK ships a migration guide when you're ready.

Nice work. Go build something.
