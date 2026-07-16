# Initiating auth

You have two metadata documents and a wide-open server. Nothing has ever been
asked for a token, so nothing has ever gone looking for one. This topic is where
the conversation starts.

It starts with a rejection, which is the part worth slowing down for. A **401 is
not a door slam** — it's the first message in a negotiation. The client asked for
something, the server said no, and then the server said *here's what to do about
it*. That second half lives in a single response header:

```
WWW-Authenticate: Bearer realm="EpicMe", resource_metadata="https://example.com/.well-known/oauth-protected-resource/mcp"
```

Read it as a sentence. *Use a bearer token. The thing you're trying to reach is
called EpicMe. If you don't have a token, everything you need to know is at this
URL.* A client that has never seen your server, that nobody configured for it,
can follow that from a bare 401 all the way to a working token — because you told
it where to look.

That's the whole trick of OAuth discovery, and it's why this topic comes before
any code that inspects a token. Before you can check a token, something has to
send you one, and nothing will send you one until you ask.

Two steps:

1. **authenticate** — reject requests to `/mcp` that arrive with no
   `Authorization` header, and give them a `WWW-Authenticate` header that says
   which scheme to use.
2. **params** — add the `resource_metadata` auth param, so the 401 points at the
   document that names your authorization server.

Fair warning about step 1: it checks that a header *exists*, not that the token
in it is any good. Anyone who types the word "Bearer" gets in. That's deliberate
— finding out what the token actually says is the next topic. For now you're
building the part that makes a client go get one.

Background worth having open: [MDN on
`WWW-Authenticate`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/WWW-Authenticate)
and [RFC 6749 §5.2](https://datatracker.ietf.org/doc/html/rfc6749#section-5.2)
for the auth params.

Run each exercise's tests from the `mcp-auth` directory, one directory at a time:

```sh
uv run pytest exercises/02.init/01.problem.authenticate
```

No server to start — the tests run the app, and the authorization server, in
process.
