# Introducing yourself

```py
def handle_oauth_protected_resource_request(request: Request) -> Response:
    return JSONResponse(
        {
            "resource": str(request.url.replace(path="/mcp", query="")),
            "authorization_servers": [AUTH_SERVER_URL],
        }
    )
```

Two keys, no network call, no `await`. For the document the entire authorization
flow pivots on, it's smaller than the CORS function.

## `request.url.replace` is the whole trick

The client reached you at some URL. `request.url` is that URL — scheme, host,
port, all of it, as observed rather than as assumed. Swap the path for `/mcp`,
drop any query string, and you have your endpoint's address expressed in terms
the caller can definitely reach.

The test looks trivial and isn't:

```py
assert metadata["resource"] == "http://testserver/mcp"
```

`testserver` is the hostname Starlette's test client invents. It isn't a real
host and it isn't in any config file — so the only way that assertion passes is
if the value came out of the request. Hardcode anything and you fail here,
immediately, instead of in a deploy.

That's the general shape of the lesson: a resource server describing itself
should describe *the way it was actually reached*, because it has no independent
knowledge of what it's called. Its hostname is something clients tell it, not
something it knows.

## Why this is the hinge

Step back and look at what you built across three exercises, in the order a
client meets it:

1. It has your URL and nothing else. It calls `/mcp`. Eventually — not yet — it
   gets a 401 pointing here.
2. It reads **this** document. Now it knows the resource it's dealing with, and
   the name of the authorization server that stands behind it.
3. It reads the authorization server's metadata, which you also serve, and learns
   where to register, where to send the user, where to trade a code for a token.

Link 2 is this file. It's the only place where "a server I've heard of" turns
into "an authorization server I can go talk to." Remove it and the chain has no
first step — the client is holding a URL that rejects it and no way to learn why
or what to do next.

And notice that `authorization_servers` is a **list**. One resource can point at
several issuers. You have one, so it's a list of one, but the shape is telling
you the relationship isn't a law of nature: the thing holding the data and the
thing vouching for users are separate on purpose, and one can answer to more than
one.

## What you haven't built

Be honest about the state of the server. `/mcp` is still wide open. You've
published a careful set of instructions explaining who guards this resource, and
nothing is guarding it. Any request still walks straight through, token or no
token.

That's the next topic. The documents come first because the 401 is only useful if
there's somewhere for it to point.
