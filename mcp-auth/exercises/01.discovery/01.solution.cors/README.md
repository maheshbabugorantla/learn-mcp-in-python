# Who's allowed to read this

One `if`, three headers:

```py
def get_cors_headers(request: Request) -> Mapping[str, str] | None:
    if "/.well-known" not in str(request.url):
        return None
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
        "Access-Control-Allow-Headers": "mcp-protocol-version",
    }
```

## The `None` is the interesting half

It's tempting to read the early return as the boring case — the case where you
didn't do anything. It's the opposite. Returning `None` is a decision: *`/mcp`
does not talk to browsers, so `/mcp` does not tell browsers they may call it.*

The failure mode CORS actually guards against is a page on `evil.example` making
a request that rides along on credentials the browser already has. Your discovery
metadata can't be abused that way — it's the same public document no matter who
asks. `/mcp` is a different animal entirely. Once there's a token involved, an
origin you never thought about being able to reach it is precisely the thing you
don't want. The cheapest way to never have that bug is to never issue the
permission.

Read the three headers as a set of narrow answers rather than a formality:

- **Origin `*`** — you genuinely cannot enumerate the origins that might read
  this, and there's nothing in it to protect. Anyone.
- **Methods `GET, HEAD, OPTIONS`** — the only verb anyone needs for a document is
  the one that reads it. No `POST`. Nothing here is writable.
- **Headers `mcp-protocol-version`** — clients are supposed to send it. Not all
  do. Allowing it costs nothing and saves a confusing preflight rejection.

## Why the 404 test passes

This is the part worth understanding, because it looks like the test is checking
the wrong thing:

```py
response = client.get("/.well-known/oauth-authorization-server")
assert response.headers.get("Access-Control-Allow-Origin") == "*"
```

There's no route for that path yet. The response is a 404 — and it has your
headers on it anyway.

Look at `WithCors` in `utils.py` and you'll see why. It doesn't consult routes;
it never knows what the app underneath decided. It calls your function with the
incoming request, and if you returned headers, it hooks the response as it starts
and stamps them on. Whatever comes back — 200, 404, and later the 401 you'll
build — gets stamped.

That ordering is deliberate, and the alternative is a real bug. If the headers
only went on successful responses, then every failure would arrive at a browser
client as an opaque nothing: the one situation where the developer most needs to
see the response body is the one where you'd have hidden it. Errors are exactly
when readability matters.

The preflight is the same idea from the other direction. `WithCors` answers
`OPTIONS` itself with a 204 and never passes it down, so a preflight to a path
that doesn't exist still gets a proper answer. The browser asks "may I?" — that
question has an answer whether or not the thing behind it is there yet.

Next: put something at that URL.
