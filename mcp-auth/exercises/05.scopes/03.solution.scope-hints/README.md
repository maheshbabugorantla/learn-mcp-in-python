# The loop closes

One key:

```py
"scopes_supported": SUPPORTED_SCOPES,
```

Small line, and it finishes something the course started in its first topic. Walk
the whole path a client takes now, with nothing configured by hand:

```
POST /mcp                  -> 401, WWW-Authenticate: resource_metadata="..."
GET  /.well-known/...      -> which authorization server, and which scopes to ask for
register, send Kody to log in with scope="entries:read tags:read"
consent screen             -> Kody sees exactly those two, and approves
POST /mcp with the token   -> 200
```

No step in that sequence involves a human editing a config file, and no step
involves anyone guessing. A client that has never heard of EpicMe reads its way
in, asks for what it needs, and gets exactly that. The 401 you wrote in `02.init`
was the first half of a sentence; `scopes_supported` is the last word of it.

## The tests are checking something real

```py
assert advertised <= set(SUPPORTED_SCOPES)   # from epicme.provider
```

That test compares what your resource server *advertises* to what your
authorization server can actually *issue*. It's not busywork. Advertise a scope
your AS won't issue and you've built a trap: the client reads your metadata, asks
for exactly what you told it to ask for, and the request fails at the
authorization server. It did everything right. Your documentation lied.

That's the standing hazard with metadata generally. It's a promise about your
server that your server doesn't check by running. It goes stale silently, and the
only person who finds out is a stranger's client at three in the morning. Both
lists here come from one source, and a test says so.

## What you built

Three steps, three places a scope lives, three different questions:

- **In the tool** — may this token do *this specific thing*? `all`, and a raise
  the model can read.
- **At the door** — can this token do *anything at all*? `any`, and a 403 that
  doesn't send the client into a refresh loop.
- **In the metadata** — what should a client *ask for*? So it never has to guess,
  and so Kody's consent screen is short and honest.

Underneath all three is the reason scopes exist at all. Not to build a permission
system. To make it possible for a person to hand an app *part* of their access,
and to know which part, at the moment they decide.

You're done with the exercises. See
[`exercises/05.scopes/FINISHED.md`](../FINISHED.md).
