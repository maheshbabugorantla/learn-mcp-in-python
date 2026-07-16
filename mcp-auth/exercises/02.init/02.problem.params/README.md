# Pointing at the instructions

Your 401 says `Bearer realm="EpicMe"` and stops. Your job: make it say where to
get a token.

## A correct dead end

Think about what a brand-new client does with your 401 today. It learns it needs
a bearer token. It does not learn what issues one, where that thing lives, or how
to register with it. So it does the only thing it can: it gives up, and a human
goes and pastes a URL into a config file somewhere.

But you already published the answer. Back in `01.discovery` you built the
protected resource metadata document — the one that names your authorization
server:

```json
{
  "resource": "https://example.com/mcp",
  "authorization_servers": ["https://auth.example.com"]
}
```

It's sitting at `/.well-known/oauth-protected-resource/mcp`, public, waiting for
someone to read it. Nobody has been told it's there.

## Auth params

The `WWW-Authenticate` header isn't just a scheme name. After the scheme come
comma-separated `key="value"` **auth params** ([RFC 6749
§5.2](https://datatracker.ietf.org/doc/html/rfc6749#section-5.2)):

```
Bearer realm="EpicMe", resource_metadata="https://example.com/.well-known/oauth-protected-resource/mcp"
```

`realm` was one. `resource_metadata` is the one that matters. With it, the 401
stops being a refusal and becomes a set of directions: read this document, find
the authorization server it names, register yourself, send the user to log in,
come back with the token. No human in the loop, no configuration, nothing about
your server known in advance.

## Build the URL, don't type it

Write a small helper for the URL, and build it from the request:

```py
def resource_metadata_url(request: Request) -> str:
    return str(
        request.url.replace(path="/.well-known/oauth-protected-resource/mcp", query="")
    )
```

Resist hardcoding a host. The same code runs on `http://localhost:3000` while
you're working and on your real domain in production, and a `resource_metadata`
pointing at localhost from a production server sends every client into a wall.
The request already knows what host it arrived on. Ask it.

Then assemble the header in `handle_unauthorized`. Build the params as a list and
join them:

```py
auth_params = [
    'Bearer realm="EpicMe"',
    f'resource_metadata="{resource_metadata_url(request)}"',
]
```

## The test follows the link

One of the two tests does something you should notice: it pulls the URL out of
your header, fetches it, and asserts the response actually contains
`authorization_servers`.

That's not pedantry. A pointer to a 404 is worse than no pointer — it costs the
client a round trip and still leaves it stuck, but now it looks like *your* bug
rather than a missing feature. If you're going to give directions, they have to
lead somewhere.

## Your task

Open `auth.py` and follow the two TODOs. `app.py` is already wired from the last
step. Then:

```sh
uv run pytest exercises/02.init/02.problem.params
```

Stuck? Diff against `exercises/02.init/02.solution.params/auth.py`.
