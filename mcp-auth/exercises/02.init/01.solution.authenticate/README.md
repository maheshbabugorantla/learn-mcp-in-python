# The server finally asks

Your server now turns away requests to `/mcp` that arrive with nothing in the
`Authorization` header, and it tells them why:

```
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="EpicMe"
```

Small change. It's the first time your server has ever asked a client for
anything.

## A middleware is a function that gets to say no first

`WithAuth` is ten lines in `utils.py`, and it's worth being able to picture:

```py
rejection = await self.authorize(Request(scope))
if rejection is not None:
    await rejection(scope, receive, send)
    return
await self.app(scope, receive, send)
```

That's it. Your `authorize` returns a `Response` and the request stops there, or
returns `None` and the MCP app never learns anything happened. Nothing in
`server.py` knows auth exists — no decorator on every tool, no check at the top
of every handler. Authorization is a property of the *edge*, not of each thing
behind it.

## Where the guard sits

```py
Mount("/mcp", app=WithAuth(mcp.streamable_http_app(), authorize)),
```

The guard wraps the mounted app, not the whole Starlette app, so the boundary is
exactly `/mcp`. Everything else in `routes` — `/healthcheck`, both `/.well-known`
documents — is untouched and public.

Keeping the metadata public is the part that looks wrong on an auth checklist and
is right anyway. The client reading it is by definition the client that doesn't
have a token yet. It's a public description of how to log in; there's nothing in
it worth protecting, and protecting it would make the flow unenterable.

## What you actually built

```py
if "authorization" not in request.headers:
    return handle_unauthorized(request)
return None
```

Read that honestly: it's a check for the presence of a header. `Bearer
hunter2` passes. `Bearer ` passes. It's a placeholder, and the test that says so
is right there in the file:

```py
def test_a_request_with_a_header_gets_through(client, token):
    """We're not checking the token yet — only that one is present."""
```

But the 401 itself isn't a placeholder — that part is real, and it's the part
that does the work. Nothing goes looking for a token until something asks for
one. You've now built the ask.

## What's still missing

`Bearer realm="EpicMe"` tells a client *what kind* of credential to send. It
doesn't tell it where to get one. A client that already has a token is fine; a
client meeting your server for the first time is stuck, holding a correct
description of a lock and no idea where the keys are made.

The next step fixes that with one more auth param.
