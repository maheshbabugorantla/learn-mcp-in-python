# Sampling

A normal tool call runs one direction. The client asks, the server answers; the
model's job is to decide *which* of your tools to call. Sampling flips that.
Mid-tool, the **server** turns around and asks the client's LLM to generate some
text — and hands the answer back into its own logic. The model isn't calling your
tool anymore; your tool is calling the model.

That's the throughline of this whole course: the server initiating a
conversation instead of only replying. Here the conversation is with the model
that's driving the session.

## Why the server would want this

You could make the caller's model do the thinking and then call a plain tool with
the result. But sometimes the tool itself needs a sentence of natural language to
finish its work — a friendly reflection to append, a few tag names to attach —
and it would be silly to make that a separate round trip the model has to
remember to take. Sampling lets the server reach for a model the way it reaches
for a database: as a helper it can call inline.

The API is one call:

```py
res = await ctx.session.create_message(
    messages=[SamplingMessage(role="user", content=TextContent(type="text", text="..."))],
    max_tokens=100,
    system_prompt="...",
)
text = getattr(res.content, "text", None)
```

You send messages, you get back a `CreateMessageResult` whose `.content` is a
content block — read its `.text`.

## The catch: not every client can answer

Sampling is optional. A client that doesn't support it has no model to run your
request, so `create_message` comes back as an error rather than text. That means
your tool has to treat "no reflection" as a normal outcome, not a failure — wrap
the call and carry on. A feature that's nice to have must never take down the
tool it's decorating.

## How the tests fake the model

There's no live LLM in the test suite. Instead the test connects a client with a
`sampling_callback` — a stand-in model that returns fixed text — so we can assert
the tool actually wove the reply into its result. And at least one test connects a
client with *no* callback at all, to prove the graceful-skip path keeps working
when nobody can answer.

Two steps, building on each other:

1. **simple** — ask the model for a one-line reflection and append it.
2. **advanced** — ask the model for tag names, then parse and attach them, turning
   a nicety into a real database change.

Run each from the course root, one directory at a time:

```sh
uv run pytest exercises/03.sampling/01.problem.simple
```

The tests run your server and a fake client in the same process — no network, no
model, nothing to start.
