# Where the tokens come from

The handler is two lines:

```py
async def handle_oauth_authorization_server_request(request: Request) -> Response:
    response = await get_http().get("/.well-known/oauth-authorization-server")
    return JSONResponse(response.json())
```

and the route that makes it reachable:

```py
Route(
    "/.well-known/oauth-authorization-server",
    handle_oauth_authorization_server_request,
),
```

## A proxy, deliberately

There's no logic in that handler, and that's the feature. Ask, receive, pass on.

The test that matters most here is the one that doesn't check any particular
field:

```py
assert client.get("/.well-known/oauth-authorization-server").json() == original
```

`original` is what the authorization server itself returns. Your copy has to be
*identical* — not compatible, not close, the same object. Which rules out the
tempting version of this code, the one that builds a dict of the fields you know
about. That version works today and lies tomorrow: the auth server adds a field,
rotates an endpoint, drops support for a grant type, and your handler keeps
confidently announcing last month's truth. A dumb pipe can't go stale.

Notice what the real document included that a hand-written one wouldn't have:

```json
"introspection_endpoint": "http://localhost:7788/oauth/introspection",
"code_challenge_methods_supported": ["S256"],
"scopes_supported": ["user:read", "entries:read", ...]
```

That `introspection_endpoint` is the payoff on discovery's promise, and it's
about to matter to *you*. In a later topic your server has to ask the auth server
what a token means. It can find that endpoint by reading this document rather
than by hardcoding a path — the same trick the clients are pulling on you, run in
the other direction.

One thing not to blur: the `scopes_supported` in there belongs to the
authorization server. It's the list of scopes it's willing to issue. That's a
different claim from *which scopes this resource requires*, which is a different
document, and which you haven't built yet.

## `async` and the shape of it

This handler is `async` for a real reason, not for decoration: it makes a network
call. Every request for your metadata becomes a request to theirs. That's a live
dependency — if the auth server is down, this endpoint fails with it. Acceptable
here, because a client that can't reach the auth server was never going to
complete a login anyway. Worth knowing you took it on.

You're now serving a document that describes *them*. The one thing still missing
is the document that describes **you** — and that's the one a client actually
starts from.
