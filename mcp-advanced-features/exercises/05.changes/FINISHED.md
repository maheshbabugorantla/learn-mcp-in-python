# You're done

You started this course with the same EpicMe journal you've been carrying since
the fundamentals — a handful of tools, a few resources, request in, response out.
It still does all of that. But it can now do the thing that request/response
alone can't: it can start the conversation.

Here's what you added:

- **Advanced tools.** Annotations, so a client can tell a reader from a destroyer
  *before* it calls — and structured output, so a result arrives as validated data
  and a text fallback in one return value, instead of JSON smuggled inside prose.
- **Elicitation.** The server pausing mid-tool to ask the *user* a question —
  "are you sure you want to delete this?" — and branching on the answer with
  `ctx.elicit(...)`.
- **Sampling.** The server asking the *client's model* to generate text with
  `ctx.session.create_message(...)`, borrowing an LLM it doesn't own to do work a
  plain function couldn't.
- **Long-running tasks.** Progress reports streamed as the work runs
  (`ctx.report_progress`), and cancellation that actually cleans up when the
  caller walks away — a `CancelledError` you catch instead of leak.
- **Changes.** The server telling the client its cached view is stale —
  list-changed for "the set is different, re-fetch," and subscriptions for "this
  one resource you're watching just moved."

## The throughline

Basic MCP is request/response: the client calls, the server answers, done. Every
feature in this course is what happens when that shape isn't enough — when the
**server** needs to speak first, mid-flight, instead of only replying.

Look at the five again and they're all the same gesture pointed different ways.
Ask the user something. Ask the model something. Report as you go. Accept a stop.
Announce a change. In each one the server stops being a passive endpoint and
becomes a participant — it interrupts, it requests, it pushes. That's the whole
category. Once you see a server as something that can initiate, these features
stop being a grab-bag of APIs and start being obvious: of course it can ask; of
course it can tell you something changed.

You see these in real clients constantly, even when they're not labeled. The
confirmation dialog before a destructive action is elicitation. The "generating…"
that streams a summary is sampling plus progress. The stop button is
cancellation. The tool list that quietly grows after you connect an integration is
list-changed. You've now built the server half of all of it.

## What this course simplified on purpose

It's worth being honest about the scaffolding, because the real world removes it:

- **The long-running task was a mock.** `video.py` doesn't touch ffmpeg — it
  sleeps in a loop and reports fractions. That was deliberate: the lesson was
  progress and cancellation, and a real encoder would have buried both under
  install instructions and platform quirks. Your progress and cancellation code is
  real; only the thing being rendered is pretend.
- **Subscriptions reached under FastMCP.** `mcp._mcp_server.subscribe_resource()`
  is the low-level `Server`, not a high-level API, because FastMCP 1.28 doesn't
  wrap this one. That's not a workaround you'll outgrow — it's just where the
  feature lives in this SDK version, and now you know the low-level server is there
  when the high-level one comes up short.
- **The other side was faked in memory.** The tests supplied a fake user through
  an `elicitation_callback` and a fake LLM through a `sampling_callback`, and
  watched notifications with a `message_handler`. No real person clicked, no real
  model ran, nothing crossed a network. That let you test server behavior in
  isolation — but a real client's user says no at inconvenient times, a real
  model is slow and occasionally wrong, and a real connection drops mid-stream.
  The code you wrote handles those; this harness just didn't make you wait for
  them.

## Where to go next

Run the solution servers against a real MCP client over stdio and watch these fire
for real — approve an elicitation yourself, cancel a render mid-progress, connect
and see a tool list grow. Then read the
[MCP specification](https://modelcontextprotocol.io/specification/2025-06-18):
the sections on notifications, elicitation, and sampling will read like a
description of things you've now built by hand.

This is the last of the four courses in the series — fundamentals, auth, UI, and
now advanced features. You've gone from a journal that handed itself to anyone, to
one that authenticates its caller, renders itself in a client, and holds up its
half of a real conversation. Go build a server that talks back.
