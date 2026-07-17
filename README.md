# Learning MCP in Python

Three hands-on courses that teach the **Model Context Protocol** by building one
thing all the way through: **EpicMe**, a personal journal an AI app can read,
write, tag, and reason about.

They're Python ports of the [EpicWeb.dev](https://www.epicweb.dev) MCP workshops,
which teach the same material in TypeScript. Everything here runs on `uv` and the
official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) —
no Node, no npm, no TypeScript.

## The three courses

They're not a single line. **[mcp-fundamentals](mcp-fundamentals)** is the base.
Then **[mcp-ui](mcp-ui)** and **[mcp-auth](mcp-auth)** are two independent
branches off it — do fundamentals first, then either one, in either order.
Neither branch requires the other: ui gives the journal a face, auth gives it
users, and they don't touch.

**[mcp-fundamentals](mcp-fundamentals)** — start here. Build an MCP server from
nothing: a server that answers a ping, then tools the model can call, resources
the app can load, and prompts a person picks from a menu. Runs on your laptop
over stdio, one user, no auth.

```sh
cd mcp-fundamentals
uv sync
uv run pytest exercises/01.ping/01.problem.connect
```

**[mcp-ui](mcp-ui)** — a branch. Give the journal a face. The same tools now
return **UI** — a tag card, a journal page, a full entry — that a UI-aware client
renders instead of showing plain text. You learn the MCP-UI sub-spec: UI
resources, the mimetype that says how to render them, and the `postMessage`
conversation once they're on screen. No auth, no users — just a screen.

```sh
cd mcp-ui
uv sync
uv run pytest exercises/01.simple/01.problem.raw-html
```

**[mcp-auth](mcp-auth)** — the other branch. Take the same journal and put it on
the internet with users in it. OAuth 2.1 metadata discovery, `WWW-Authenticate`,
token introspection, per-user data scoping, and scopes — implemented by hand, so
you know what the machinery does before you let a library do it for you.

```sh
cd mcp-auth
uv sync
uv run pytest exercises/01.discovery/01.problem.cors
```

Each course is a standalone project with its own `pyproject.toml` and its own
virtualenv. Do fundamentals first — both branches assume you already know what a
tool is.

## How they work

Every exercise is a **problem** directory and a **solution** directory. Read the
problem's `README.md`, fill in the `TODO`s until the tests pass, and diff against
the solution when you're stuck. Run one directory at a time.

The tests are the feedback loop, and they need nothing running — no servers, no
subprocesses, no ports.

## Credit and license

Python ports of [**mcp-fundamentals**](https://github.com/epicweb-dev/mcp-fundamentals),
[**mcp-ui**](https://github.com/epicweb-dev/mcp-ui), and
[**mcp-auth**](https://github.com/epicweb-dev/mcp-auth) by Kent C. Dodds. The
exercise structure and the EpicMe idea are theirs; the Python code and all lesson
text here were written fresh for these ports.

If TypeScript is your language, go do the originals — they're excellent, and they
come with a proper workshop app.

Licensed **GPL-3.0**, matching upstream. Upstream asks you to contact
team@epicweb.dev before running workshops with the material — worth honoring if
you ever teach this to a group rather than working through it yourself.
