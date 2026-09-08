# Ask what the token means

Your `authorize` guard currently reads, in full:

```py
if "authorization" not in request.headers:
    return handle_unauthorized(request)
```

Send `Authorization: Bearer hunter2` and you're in. That's not a check, it's a
formality. Time to make it real.

## You can't read the token

The instinct is to open the token up and look. You can't. The one your tests hold
looks like this:

```
Bearer 8xJ2mQvK3nR7pL1wY6tZ4cF9hB0sD5gA
```

That's `secrets.token_urlsafe(32)` and nothing more — a coin flip, 32 bytes of
it. There's no user encoded in it, no expiry, no scopes, no structure to parse.
The authorization server generated it, wrote down what it stands for, and handed
you the string. It's a coat check ticket. The number on the ticket doesn't
describe your coat.

So there's exactly one way to find out what it means: **ask the server that
issued it.** That question is called introspection, and it's
[RFC 7662](https://datatracker.ietf.org/doc/html/rfc7662).

## The request

The authorization server has an endpoint waiting at `/oauth/introspection`. It's
a form POST, not JSON — the RFC predates the JSON-everywhere habit:

```py
response = await get_http().post("/oauth/introspection", data={"token": token})
```

`get_http()` is already pointed at the authorization server, so a relative path
is all you need. Under pytest it's wired to call that server in the same process,
which is why you don't have to start anything.

The answer, for a live token:

```json
{ "active": true, "sub": "user-kody", "client_id": "test-client", "scope": "entries:read tags:read" }
```

Three fields carry the weight. `sub` — "subject" — is the user id. `client_id` is
which app is calling. `scope` is the permissions, and note it's **one
space-separated string**, not a list. Splitting it is your job, and `auth.py` is
the last place that should have to care about that wire format.

## Say no the same way every time

`resolve_auth_info` returns `AuthInfo | None`, and `None` is doing something
deliberate. No header, a header that isn't Bearer, an empty Bearer, a non-200
from introspection — all of them return the same `None`. Not different errors,
not a reason code.

That's the correct instinct for auth generally: **never leak why a token failed.**
A caller who learns the difference between "unknown token" and "expired token"
has learned something about which tokens exist. Give every failure the same
blank stare.

## Your task

Open `auth.py` and follow the two TODOs: model the introspection response, then
write `resolve_auth_info`. Then open `app.py` and let `authorize` use it.

```sh
uv run pytest exercises/03.auth-info/01.problem.introspect
```

One thing will still be broken when the tests pass, and it's worth knowing now:
your `ActiveToken` model requires `client_id`, `scope` and `sub`, but a token the
server doesn't recognize comes back as `{"active": false}` — no other fields at
all. Validation explodes, and the client gets a 500. Nothing here tests that yet.
The next step is where it gets fixed.

Stuck? Diff against `exercises/03.auth-info/01.solution.introspect/`.

## What's next?

Next you handle the answer you haven't modelled yet. An expired token gets a
perfectly valid reply from the introspection endpoint — just not the shape you
told pydantic to expect, which reaches the caller as a 500 rather than a 401.
