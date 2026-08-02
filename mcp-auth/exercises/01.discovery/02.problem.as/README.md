# Where the tokens come from

Your 404 is readable now. Time to make it a 200.

`/.well-known/oauth-authorization-server` is the document described by
**RFC 8414**, and it's the authorization server's answer to every question a
client has about how to log a user in. Where do I send the browser? Where do I
exchange the code for a token? Can I register myself, and at what URL? It's a
flat JSON object, and it looks like this:

```json
{
  "issuer": "http://localhost:7788/",
  "authorization_endpoint": "http://localhost:7788/authorize",
  "token_endpoint": "http://localhost:7788/token",
  "registration_endpoint": "http://localhost:7788/register",
  ...
}
```

Every one of those URLs is something a client would otherwise need a human to
configure. Because the document exists, it doesn't.

## You're forwarding, not writing

Here's the thing to be clear about before you type anything: this document is
**not yours**. It describes the authorization server — its endpoints, its
capabilities, its opinions about PKCE. The authorization server already publishes
it. You are not going to invent one.

You're going to fetch theirs and pass it along:

```py
response = await get_http().get("/.well-known/oauth-authorization-server")
return JSONResponse(response.json())
```

`get_http()` comes from `epicme.client` and is already pointed at the
authorization server, so a path is all you need. (Worth thirty seconds in that
file: it's a function rather than a client object precisely so the tests can
swap in an in-process auth server, which is why none of this needs a running
server or a port.)

The test pins this down — it fetches the document straight from the auth server
and asserts yours is byte-for-byte the same object. Forward it. Don't improve it.
The moment you start editing fields on the way through, you're publishing claims
about a server you don't control, and the two documents drift the first time it
changes.

## So why serve it at all?

Fair question, and the honest answer is: strictly, you don't have to. A client
that reads your *protected resource* metadata (the next exercise) learns the
authorization server's URL and could go fetch this from the source.

But some clients look on your host first, before they've read anything else. It's
three lines to say yes to them instead of handing back a 404.

## Your task

This one touches two files.

Open `auth.py` and write `handle_oauth_authorization_server_request`. Then open
`app.py`, import it, and add its `Route` to the list. A handler nothing routes to
is a handler nobody calls.

```sh
uv run pytest exercises/01.discovery/02.problem.as
```

Stuck? Diff against `exercises/01.discovery/02.solution.as/`.

## What's next?

Next comes the other document, the one about your own server. It is shorter, but
it has a wrinkle this one didn't: the resource identifier has to be built from
the request that asked for it, not typed in as a constant.
