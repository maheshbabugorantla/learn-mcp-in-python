# MCP Fundamentals — in Python

> Start here. When you're done, three courses build on this same journal, and you
> can take them in any order: [**mcp-auth**](../mcp-auth) puts it on the internet
> and gives it users, [**mcp-ui**](../mcp-ui) gives it a face — tools that send UI
> a client can render — and [**mcp-advanced-features**](../mcp-advanced-features)
> teaches the server to speak first: elicitation, sampling, progress and
> cancellation, and change notifications.

Learn the **Model Context Protocol** by building a real MCP server: EpicMe, a
personal journal that an AI app can read, search, tag, and reason about.

MCP is a standard way for apps like Claude Desktop, Cursor, and ChatGPT to talk
to code you wrote. You run a **server**; the AI app is a **client**. Write one
MCP server, and every client that speaks the protocol can use it — no per-app
integration.

By the end you'll have a server with tools, resources, and prompts, running
against a real AI client.

## Setup

You need [`uv`](https://docs.astral.sh/uv/getting-started/installation/). It
handles Python itself, so that's the only prerequisite.

```sh
uv sync
```

That's it. No Node, no npm, no TypeScript.

## How to work through it

Each exercise is a **problem** directory and a **solution** directory. You work
in the problem: open its `README.md`, read the lesson, then fill in the `TODO`s
in `server.py` until the tests pass.

```sh
uv run pytest exercises/01.ping/01.problem.connect
```

Run **one directory at a time** — every exercise has its own `server.py`, so
pytest can't collect them all at once. Stuck? The solution next door has the
answer; diff it against yours.

Start at `exercises/01.ping/README.md` and go in order. Each topic builds on the
last.

## The exercises

| # | Topic | What you learn |
|---|-------|----------------|
| 01 | [ping](exercises/01.ping) | Create a server, run it over stdio, answer a ping |
| 02 | [tools](exercises/02.tools) | Functions the model can call: schemas from type hints, errors as messages |
| 03 | [resources](exercises/03.resources) | Data the app can load: static, templates, collections, completion |
| 04 | [resource-tools](exercises/04.resource-tools) | Tools that return resources — embedded vs. linked |
| 05 | [prompts](exercises/05.prompts) | Templates a person picks from a menu, carrying their own context |

The three primitives, and the question that separates them — **who decides?**

- A **tool** is what the *model* decides to call.
- A **resource** is what the *application* decides to load.
- A **prompt** is what a *person* picks from a menu.

## What's in a directory

```
exercises/03.resources/01.problem.simple/
  README.md        the lesson — read this first
  server.py        your work goes here
  test_server.py   run it; it tells you what's missing
  db.py            the journal database (infrastructure, never edit)
```

`db.py` is a small stdlib `sqlite3` wrapper, identical in every exercise that uses
it, so the only thing changing between steps is the MCP code you write.

## The MCP Inspector (optional)

A browser UI for calling your tools and reading your resources by hand:

```sh
cd exercises/01.ping/01.solution.connect
uv run mcp dev server.py
```

This shells out to `npx`, so it's the one thing here that needs Node. It's
genuinely useful, but the tests are the primary feedback loop — you never need
the Inspector to finish an exercise.

## A note on SDK versions

This course pins **`mcp==1.28.1`** and uses the `FastMCP` API:

```py
from mcp.server.fastmcp import FastMCP
```

A **v2 is currently in beta**. It renames `FastMCP` to `MCPServer` and moves the
protocol types into a separate `mcp_types` package. If you find SDK docs or
examples that `import` things this course doesn't, that's why — check whether
you're reading v1 or v2 docs. Everything you learn here carries over; the imports
move. The pin in `pyproject.toml` keeps this course stable in the meantime.

## Credit and license

This is a Python port of
[**mcp-fundamentals**](https://github.com/epicweb-dev/mcp-fundamentals) by
[Epic AI](https://www.epicai.pro) (Kent C. Dodds), which teaches the same
curriculum in TypeScript. The exercise structure and the EpicMe journal idea come
from that workshop; the Python code and lesson text here were written fresh for
this port.

If TypeScript is your language, go do the original — it's excellent, and it comes
with a proper workshop app.

Licensed **GPL-3.0**, matching upstream. Note that upstream asks you to contact
team@epicweb.dev before running workshops with the material — worth honoring if
you ever teach this to a group rather than working through it yourself.
