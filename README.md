# Learn MCP in Python

[![tests](https://github.com/maheshbabugorantla/learn-mcp-in-python/actions/workflows/ci.yml/badge.svg)](https://github.com/maheshbabugorantla/learn-mcp-in-python/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
[![uv](https://img.shields.io/badge/managed%20with-uv-261230)](https://github.com/astral-sh/uv)

Four hands-on courses that teach the **Model Context Protocol** by building one
thing all the way through: **EpicMe**, a personal journal an AI app can read,
write, tag, and reason about.

They're Python ports of the [EpicWeb.dev](https://www.epicweb.dev) MCP workshops,
which teach the same material in TypeScript. Everything here runs on `uv` and the
official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) —
no Node, no npm, no TypeScript.

## Prerequisites

You need [**`uv`**](https://docs.astral.sh/uv/) — that's the only prerequisite. It
installs and manages Python itself, so you don't need a separate Python 3.10+.

```sh
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Node is **not** required. (The one optional exception is the MCP Inspector in the
fundamentals course, `uv run mcp dev server.py`, which shells out to `npx` — the
tests never need it.)

## Quickstart

On macOS or Linux, a `Makefile` wraps everything:

```sh
make install   # install every course's dependencies (uv sync)
make test      # run all 41 solution suites across the four courses
make demo      # launch the mcp-ui browser demo at http://localhost:8788
make help      # list every target
```

No `make` (e.g. Windows)? Do it per course — each is an independent `uv` project:

```sh
cd mcp-fundamentals
uv sync
uv run pytest exercises/01.ping/01.problem.connect
```

## The four courses

They're not a single line. **[mcp-fundamentals](mcp-fundamentals)** is the base.
Then **[mcp-auth](mcp-auth)**, **[mcp-ui](mcp-ui)**, and
**[mcp-advanced-features](mcp-advanced-features)** are three independent branches
off it — do fundamentals first, then any of the three, in any order. None of them
requires the others: auth gives the journal users, ui gives it a face, and
advanced-features gives it the server-initiated parts of the protocol. They don't
touch.

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

**[mcp-advanced-features](mcp-advanced-features)** — a branch. Basic MCP is
request/response: the client calls, the server answers. Here the **server**
starts the conversation instead — it asks the user to confirm before a delete
(elicitation), asks the client's model to write a reflection (sampling), reports
progress through slow work and accepts a cancel, and announces when something
changed so the client looks again (list-changed and subscriptions). Same journal,
no auth, no browser — just the parts of the protocol where the server speaks
first.

```sh
cd mcp-advanced-features
uv sync
uv run pytest exercises/02.elicitation/01.problem
```

Each course is a standalone project with its own `pyproject.toml` and its own
virtualenv. Do fundamentals first — all three branches assume you already know
what a tool is.

## How the exercises work

Every exercise is a **problem** directory and a **solution** directory. Read the
problem's `README.md`, fill in the `TODO`s in `server.py` until the tests pass,
and diff against the solution when you're stuck.

The tests are the feedback loop, and they need nothing running — no servers, no
subprocesses, no ports. They spin up an in-memory MCP client wired to your server
and check what it returns.

## Repository layout

```
.
├── mcp-fundamentals/        # the base course
├── mcp-auth/                # branch: users + OAuth 2.1
├── mcp-ui/                  # branch: UI resources (+ a runnable browser demo)
├── mcp-advanced-features/   # branch: elicitation, sampling, progress, changes
├── scripts/test.sh          # runs every course's solution suites
├── Makefile                 # install / test / demo / clean
├── .github/workflows/ci.yml # runs all solution suites on push
└── README.md
```

Each `<course>/` holds `pyproject.toml`, `uv.lock`, a course `README.md`, and an
`exercises/` tree of `NN.topic/NN.{problem,solution}.<slug>/` directories.

## Running the tests

```sh
make test                 # all four courses
make test-fundamentals    # one course
make test-ui
# …or directly:
./scripts/test.sh mcp-auth
```

Tests run **one directory at a time**, on purpose. Each course is a separate `uv`
project, and within a course every exercise dir has its own `server.py` /
`test_server.py` — the same module names in every dir — so pytest can't collect a
whole course in one pass. `scripts/test.sh` handles this by running each solution
suite in turn; the same script backs the Makefile and CI. (Problem directories are
*meant* to fail until you finish them, so the sweep runs the solutions.)

## Dependencies: runtime vs. dev

Each course uses `uv`'s dependency groups to separate the two:

- **Runtime** (`[project].dependencies`): just **`mcp==1.28.1`** — the only thing
  the MCP server you build needs to run. Starlette, uvicorn, httpx, and pydantic
  come with the SDK, so the auth server and the ui demo use them without adding
  anything of their own.
- **Dev** (`[dependency-groups].dev`): **`pytest`** and **`pytest-asyncio`**, the
  test runner that drives the exercises (plus the `mcp[cli]` Inspector in
  fundamentals). `pytest-asyncio` is here because the MCP client sessions are
  async; `asyncio_mode = "auto"` lets the `async def test_...` functions run
  without ceremony.

`uv sync` installs both groups (so the tests just work). Want only what a
deployed server needs? `uv sync --no-dev`.

## Contributing

This is a teaching repository, so the bar is: keep it clear and keep it green.
Prose is written fresh (not translated from the upstream workshops — see the
license note), and `make test` must stay at 41/41 before anything lands.

## Credit and license

Python ports of [**mcp-fundamentals**](https://github.com/epicweb-dev/mcp-fundamentals),
[**mcp-auth**](https://github.com/epicweb-dev/mcp-auth),
[**mcp-ui**](https://github.com/epicweb-dev/mcp-ui), and
[**advanced-mcp-features**](https://github.com/epicweb-dev/advanced-mcp-features)
by Kent C. Dodds. The exercise structure and the EpicMe idea are theirs; the
Python code and all lesson text here were written fresh for these ports.

If TypeScript is your language, go do the originals — they're excellent, and they
come with a proper workshop app.

Licensed **GPL-3.0**, matching upstream. Upstream asks you to contact
team@epicweb.dev before running workshops with the material — worth honoring if
you ever teach this to a group rather than working through it yourself.
