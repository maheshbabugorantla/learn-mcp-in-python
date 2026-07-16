# Asking for a token

Your `/mcp` endpoint answers anyone who calls it. Your job: make it ask who's
calling.

## Say no in a way the client can use

A 401 with an empty body is a dead end. The client knows it failed and knows
nothing else. So HTTP gives you a header for the rest of the sentence:

```
WWW-Authenticate: Bearer realm="EpicMe"
```

Two pieces. `Bearer` is the **scheme** — it tells the client what kind of
credential to send, and how (`Authorization: Bearer <token>`). `realm` is a label
for the protected area. It exists for people: a client can show it to a human so
they know *what* is asking them to log in. When a request passes through a proxy,
a gateway and your server, "EpicMe" is what says this one is yours.

That header goes in `handle_unauthorized`:

```py
return Response(
    "Unauthorized",
    status_code=401,
    headers={"WWW-Authenticate": 'Bearer realm="EpicMe"'},
)
```

## Deciding who gets in

`utils.py` gives you `WithAuth`, a middleware that runs a function of yours
before the app underneath sees the request. The contract is small: return a
`Response` to reject, return `None` to allow.

```py
async def authorize(request: Request) -> Response | None:
    if "authorization" not in request.headers:
        return handle_unauthorized(request)
    return None
```

Then wrap the mounted MCP app with it in `routes`:

```py
Mount("/mcp", app=WithAuth(mcp.streamable_http_app(), authorize)),
```

## This is not authentication

Be clear-eyed about what you just wrote. It checks that *a* header showed up. Not
that the token is valid, not that it's for this server, not that it hasn't
expired. `Authorization: Bearer hello` gets in.

That's fine, for now — inspecting the token is `03.auth-info`. But the header
check isn't a throwaway either. It's the first move of every OAuth flow, and it's
the move that starts the flow: until something gets a 401, no client has any
reason to go find a token. You're building the ask; the checking comes next.

## What stays public

Notice the mount is `/mcp` exactly, so the guard covers that path and nothing
else. `/healthcheck` and both `/.well-known` documents stay open, and they have
to. The client that gets your 401 is a client with no token — which is precisely
the client that needs to read the metadata explaining how to get one. Lock the
metadata behind a token and the only way in is to already be in.

(Mounting at `/` instead would also mean every typo a client makes returns a 401
demanding a token instead of an honest 404.)

## Your task

Open `auth.py` and write `handle_unauthorized`, then open `app.py` and write
`authorize` and wire it into the mount. Then:

```sh
uv run pytest exercises/02.init/01.problem.authenticate
```

The tests check that a bare request is rejected, that the 401 carries the header,
that a request with *any* Authorization header gets through, and that discovery
stayed public.

Stuck? Diff against `exercises/02.init/01.solution.authenticate/`.
