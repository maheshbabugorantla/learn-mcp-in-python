# MCP Auth — in Python

Build a **remote MCP server with users**: one that a stranger's AI client can
discover, log into, and use — without you configuring anything on either end.

This is the sequel to [MCP Fundamentals](../mcp-fundamentals). There, EpicMe was
a journal with one user, running on your laptop over stdio. Here it's an HTTP
server with real users, real access tokens, and real permissions. The journal is
the same. Everything around it changes.

By the end you'll have implemented the OAuth 2.1 side of the MCP spec by hand:
metadata discovery, `WWW-Authenticate`, token introspection, per-user data
scoping, and scopes.

## Setup

You need [`uv`](https://docs.astral.sh/uv/getting-started/installation/). It
handles Python itself, so that's the only prerequisite.

```sh
cd mcp-auth
uv sync
```

That's it. No Node, no npm, no TypeScript.

## How to work through it

Each exercise is a **problem** directory and a **solution** directory. You work
in the problem: open its `README.md`, read the lesson, then fill in the `TODO`s
until the tests pass.

```sh
uv run pytest exercises/01.discovery/01.problem.cors
```

Run **one directory at a time** — every exercise has its own `app.py`, so pytest
can't collect them all at once. Stuck? Diff the solution next door against yours.

Start at `exercises/01.discovery/README.md` and go in order.

**You don't need to start a server.** The tests run your app and the
authorization server in the same process, over no sockets at all.

## The exercises

| # | Topic | What you learn |
|---|-------|----------------|
| 01 | [discovery](exercises/01.discovery) | How a client finds out who issues tokens for you — CORS, and the two metadata documents |
| 02 | [init](exercises/02.init) | Turning a 401 into instructions with `WWW-Authenticate` |
| 03 | [auth-info](exercises/03.auth-info) | Introspection: asking the authorization server what an opaque token means |
| 04 | [user](exercises/04.user) | Getting the caller to your tools, and scoping every query to them |
| 05 | [scopes](exercises/05.scopes) | What a token is *allowed* to do, and saying no usefully |

## What's in a directory

```
exercises/03.auth-info/01.problem.introspect/
  README.md        the lesson — read this first
  auth.py          your work goes here — everything about who's calling
  app.py           your work goes here — the routes and the guard
  server.py        the MCP server: tools, resources, the prompt
  utils.py         two bits of ASGI plumbing (given)
  test_app.py      run it; it tells you what's missing
  conftest.py      test fixtures (given)
```

Two files carry the course: **`auth.py`** grows from "where is the auth server"
to a full token-to-user-to-permissions pipeline, and **`app.py`** decides what's
public and what isn't.

## The other half: `src/epicme/`

The journal database and the **EpicMe authorization server** live here. You
import from them; you never edit them.

The authorization server is the thing your server keeps talking to. It holds the
users and issues the tokens; your MCP server holds the journal. Keeping them
apart is the whole reason discovery and introspection exist — if one process did
both, it could just look in a variable.

It's a real OAuth 2.1 server (built on the SDK's own `create_auth_routes`), with
two users, `kody` and `olivia`, and no passwords — you pick who you are on the
consent screen. Two users, so you can prove one can't read the other's journal.

## Running it for real

Two terminals. First the authorization server:

```sh
uv run epicme-auth          # http://localhost:7788
```

Then your MCP server:

```sh
cd exercises/05.scopes/03.solution.scope-hints
uv run uvicorn app:app --port 8788
```

Point an MCP client at `http://localhost:8788/mcp` and it will walk the whole
flow you built: get a 401, read your metadata, find the authorization server,
register itself, send you to the consent screen, and come back with a token.

## Two places this differs from the TypeScript workshop

Both are called out again in the lessons where they land.

**Scopes don't hide tools.** Upstream registers tools per connection, so a user
without `tags:read` never sees the prompt. FastMCP registers tools once at import
time, so here the list is the same for everyone and the scope check happens when
a tool is *called*. Per-request filtering needs private SDK internals in v1.28,
which isn't worth teaching.

**Topic 03's last two steps are swapped.** Upstream goes introspect → error →
active, which leaves a step where an invalid token causes a 500. This port goes
introspect → active → error, so an invalid token gets a clean 401 before you
polish what the 401 says.

The journal database is also local sqlite scoped by user id, rather than living
behind an HTTP API on the auth server. The lesson — every query is scoped to the
authenticated user — is the same; the plumbing is shorter.

## A note on SDK versions

This course pins **`mcp==1.28.1`**, the same as the fundamentals course. A **v2
is in beta** which renames `FastMCP` to `MCPServer` and moves the protocol types
into a separate `mcp_types` package. If you find SDK docs that import things this
course doesn't, check whether you're reading v1 or v2.

The SDK is the only dependency. Starlette, httpx and pydantic all arrive with it,
so this course uses them without adding anything of its own.

Worth knowing early: the SDK *can* do a lot of this for you. `AuthSettings` and
`TokenVerifier` will generate the protected resource metadata, return the 401,
and enforce scopes. We're building it by hand because in an auth course the
mechanics **are** the lesson — the point isn't a working server, it's knowing
what the working server is doing. `FINISHED.md` shows you the shortcut once
you've earned it.

## Credit and license

This is a Python port of
[**mcp-auth**](https://github.com/epicweb-dev/mcp-auth) by
[Epic AI](https://www.epicai.pro) (Kent C. Dodds), which teaches the same
curriculum in TypeScript on Cloudflare Workers. The exercise structure and the
EpicMe idea come from that workshop; the Python code and lesson text here were
written fresh for this port.

If TypeScript is your language, go do the original — it's excellent, and it comes
with a proper workshop app.

Licensed **GPL-3.0**, matching upstream. Upstream asks you to contact
team@epicweb.dev before running workshops with the material — worth honoring if
you ever teach this to a group rather than working through it yourself.
