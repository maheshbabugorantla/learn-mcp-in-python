# MCP Advanced Features — in Python

> Build on [**mcp-fundamentals**](../mcp-fundamentals). You already have a
> journal an AI app can read, write, tag, and reason about. Here you teach the
> **server** to start the conversation — to ask, report, and announce, instead
> of only answering.

Basic MCP is request/response: the client calls a tool, the server answers, done.
This course is everything that happens when one answer isn't enough — when the
**server**, mid-tool, needs to reach back to the other side:

- **ask the user** something before it acts (elicitation),
- **ask the client's model** to write something (sampling),
- **report** as it grinds through slow work (progress),
- **accept a "stop"** partway through (cancellation),
- or **announce** that something changed, so the client looks again
  (list-changed and subscriptions).

Every feature here is the server initiating, in the middle of a call, rather than
just replying to one.

This course reuses the EpicMe journal from mcp-fundamentals — the same entries,
tags, and CRUD tools — and each topic bolts one advanced capability onto it. It
does **not** require [mcp-auth](../mcp-auth) or [mcp-ui](../mcp-ui): no users, no
OAuth, no browser. Just the single-user journal and the parts of the protocol
where the server speaks first.

## Setup

You need [`uv`](https://docs.astral.sh/uv/getting-started/installation/). It
handles Python itself, so that's the only prerequisite.

```sh
uv sync
```

That's it. No Node, no npm, no TypeScript. Everything is Python on the official
[MCP SDK](https://github.com/modelcontextprotocol/python-sdk) (`mcp==1.28.1`,
the `FastMCP` API).

## How to work through it

Each exercise is a **problem** directory and a **solution** directory. You work
in the problem: open its `README.md`, read the lesson, then follow the `TODO`s in
`server.py` until the tests pass.

```sh
uv run pytest exercises/02.elicitation/01.problem
```

Run **one directory at a time** — every exercise has its own `server.py`, so
pytest can't collect them all at once. Stuck? Diff your `server.py` against the
sibling `*.solution*` dir next door.

One thing to expect: an unfinished step raises a `NotImplementedError` placeholder
where the feature belongs (or simply omits it). So the first thing you see isn't a
clean "not done yet" — it's a failing **assertion**: the test asked for a
reflection, a progress event, or a notification that isn't there yet. That failure
is the spec. It clears the moment you build the feature the TODOs describe.

## How the tests fake the other side

Every feature here needs a counterpart — a user to answer, a model to generate, a
client to receive notifications. None of that is real. The tests spin up an
**in-memory client** wired to the server directly (no network, no ports) and hand
it stand-ins for whatever the topic needs:

- **elicitation** — an `elicitation_callback`, a fake user that answers a
  confirmation with accept or decline.
- **sampling** — a `sampling_callback`, a fake LLM that returns canned text so the
  tool has something to weave in.
- **progress** — a `progress_callback` passed to `call_tool`, which collects each
  progress event the tool emits.
- **cancellation** — the call is wrapped in `anyio.move_on_after(...)`, so the test
  cancels the tool mid-render and then checks its cleanup ran.
- **changes** — a `message_handler`, a callback that sees every notification the
  server sends, so the test can assert the right one arrived.

Because the fakes live in the test, you never need a real client or a real model
to finish an exercise.

## The exercises

| # | Topic | What you build |
|---|-------|----------------|
| 01 | [advanced-tools](exercises/01.advanced-tools) | Tool **annotations** (`ToolAnnotations` — readOnly / destructive / idempotent hints), then **structured output**: give a tool a pydantic return type and the result carries `structuredContent`, not just prose |
| 02 | [elicitation](exercises/02.elicitation) | The server pauses mid-tool with `ctx.elicit(message, schema=...)` to ask the user to confirm before a delete goes through |
| 03 | [sampling](exercises/03.sampling) | The server asks the client's LLM to generate text via `ctx.session.create_message(...)` — a simple reflection first, then an advanced multi-step use |
| 04 | [long-running-tasks](exercises/04.long-running-tasks) | **Progress**: a slow render reports fractions with `ctx.report_progress(...)`. Then **cancellation**: the same render cleans up when the caller gives up |
| 05 | [changes](exercises/05.changes) | Tell the client "look again": tools **list-changed**, then **resources list-changed**, then per-resource **subscriptions** with `send_resource_updated(...)` |

Within a topic the steps build on each other — structured output extends the
annotated server, advanced sampling extends the simple one, cancellation extends
progress, and each step of `05.changes` extends the last. Across topics, each one
starts fresh from the same base journal, so you can pick a topic that interests
you without having done the others.

## Two honest divergences

**Topic 04 fakes the video render.** Upstream shells out to `ffmpeg` to build a
"year in review" clip. That's irrelevant to the lesson, which is purely about
progress and cancellation — so `video.py` is a mock that sleeps in a loop and
reports fractions. Your tool's one job is to feed those fractions to the client
and to clean up when cancelled; whether the bytes underneath are real video
doesn't change any of that.

**Topic 05's subscriptions reach the low-level server.** FastMCP (1.28) wraps
almost everything, but it does **not** wrap resource subscriptions — there's no
`@mcp.subscribe` decorator. The subscribe/unsubscribe handlers live on the
low-level `Server` that FastMCP is built on, reached via
`mcp._mcp_server.subscribe_resource()`. That's not a blessed high-level API, and
the exercise says so — but it's the real answer in this SDK version, and it shows
you the machinery FastMCP delegates to underneath.

## Credit and license

This is a Python port of
[**advanced-mcp-features**](https://github.com/epicweb-dev/advanced-mcp-features)
by [Epic AI](https://www.epicai.pro) (Kent C. Dodds), which teaches the same
material in TypeScript. The exercise structure and the EpicMe journal come from
that workshop; the Python code and all lesson text here were written fresh for
this port.

If TypeScript is your language, go do the original — it's excellent, and it comes
with a proper workshop app.

Licensed **GPL-3.0**, matching upstream. Upstream asks you to contact
team@epicweb.dev before running workshops with the material — worth honoring if
you ever teach this to a group rather than working through it yourself.
