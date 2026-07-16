# A 401 that leads somewhere

Your rejection now carries directions:

```
WWW-Authenticate: Bearer realm="EpicMe", resource_metadata="http://testserver/.well-known/oauth-protected-resource/mcp"
```

One auth param. It changes what the response *is*. Before, it was a refusal.
Now it's an onboarding.

## Follow the chain

Walk it as a client that has never heard of your server:

1. Call `/mcp`. Get a 401 with that header.
2. Read `resource_metadata`. Fetch the URL.
3. The document names `authorization_servers`. Go there.
4. Register, send the user to log in, get a token.
5. Call `/mcp` again with `Authorization: Bearer <token>`.

Every link in that chain came from the one before it. Nothing was configured
ahead of time; the client started with a URL and a 401 and found the rest. That's
the property that makes MCP servers something a client can just *connect to* —
and every piece of it is either a document you published in `01.discovery` or the
header you just wrote.

## The URL comes from the request

```py
def resource_metadata_url(request: Request) -> str:
    return str(
        request.url.replace(path="/.well-known/oauth-protected-resource/mcp", query="")
    )
```

The request already carries the scheme and host it arrived on, so the same
function is correct on localhost and correct in production. Note how the tests
see `http://testserver` — no config, no env var, no branch. A hardcoded host
would be one more thing to get wrong at deploy time, and the failure mode is
nasty: everything works locally, and in production every client gets pointed at a
machine that isn't there.

`.replace(path=..., query="")` reuses the request's URL and swaps the parts that
change. Dropping the query string matters — metadata URLs shouldn't inherit
whatever was on the request that got rejected.

## Params are a list you join

```py
auth_params = [
    'Bearer realm="EpicMe"',
    f'resource_metadata="{resource_metadata_url(request)}"',
]
headers={"WWW-Authenticate": ", ".join(auth_params)}
```

Building a list and joining it is nicer than concatenating a string, and it's the
shape you want when there are more params to add. The comma-space separator is
what [RFC 6749
§5.2](https://datatracker.ietf.org/doc/html/rfc6749#section-5.2) asks for.

## The pointer has to be real

The second test doesn't take your word for it:

```py
url = header.split("resource_metadata=")[1].split(",")[0].strip().strip('"')
metadata = client.get(url)
assert metadata.status_code == 200
assert "authorization_servers" in metadata.json()
```

It follows the link and reads what's there. A `resource_metadata` pointing at a
404 is worse than none at all — you've sent a client somewhere with confidence,
and it arrives to find nothing. Directions are only worth giving if they lead
somewhere.

## Still a placeholder underneath

Your front door is now complete in one direction: a client with no token can find
its way to getting one. In the other direction it's still wide open. `authorize`
checks that a header is present, and `Bearer anything` is a present header.

Next topic: read the token, find out who's actually calling, and give a bad token
the answer it deserves.
