# Scopes

Your server knows who's calling and serves them their own journal. Two questions
look alike and aren't: *who are you* and *what may you do*. Everything up to now
answered the first one. This topic is the second.

Here's the thing the first question can't handle. Kody wants an AI client to
suggest tags for his entries. To do that it needs to read his entries and his
tags. It does not need to write new entries, and it certainly doesn't need his
email address. But a token that says "this is Kody" says nothing about *which
parts of being Kody* the client gets. It's all of it or none of it, and every app
Kody ever tries gets his whole diary.

A **scope** is how that stops being binary. When Kody sends a client off to log
in, the client names the scopes it wants; the consent screen shows Kody exactly
those; Kody approves, and the token comes back carrying only what he agreed to.
The client gets *some* of Kody's access rather than all of it. That's the whole
idea, and it's why the same login can produce two tokens with very different
powers.

There are five scopes in EpicMe:

```
user:read  entries:read  entries:write  tags:read  tags:write
```

That shape — `resource:action` — isn't in any spec. It's a convention, and a good
one: the resource names what you're touching, the action names what you're doing
to it, and a person reading a consent screen can tell `entries:read` from
`entries:write` without a glossary. Other servers use `repo`, `admin`,
`read:org`. Pick a pattern and hold it; the audience for these strings is a human
deciding whether to click yes. [RFC 6749
§3.3](https://datatracker.ietf.org/doc/html/rfc6749#section-3.3) defines them as
a space-separated list of case-sensitive strings the server makes up, and that's
genuinely all the spec has to say. The [MCP authorization
spec](https://modelcontextprotocol.io/specification/draft/basic/authorization)
builds on that with the discovery documents you already wrote.

The interesting part is that scopes show up in three different places in your
code, for three different reasons:

1. **check-scopes** — inside each tool: may this token do this specific thing?
2. **validate-sufficient-scope** — at the front door: can this token do anything
   here at all?
3. **scope-hints** — in your metadata: what should a client ask for in the first
   place?

Run each exercise's tests from the `mcp-auth` directory, one directory at a time:

```sh
uv run pytest exercises/05.scopes/01.problem.check-scopes
```

No server to start — the tests run your app, and the authorization server, in
process.

## What's next?

This is the last topic. After it, `mcp-ui` and `mcp-advanced-features` branch off
the same fundamentals base in either order — neither one needs any of the auth
machinery you built here.
