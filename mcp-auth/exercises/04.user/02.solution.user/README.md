# Asking the server that knows

Five lines:

```py
async def fetch_user(auth_info: AuthInfo) -> User | None:
    """Ask the authorization server who this token belongs to."""
    response = await get_http().get(
        "/oauth/userinfo", headers={"Authorization": f"Bearer {auth_info.token}"}
    )
    if response.status_code != 200:
        return None
    return User.model_validate(response.json())
```

Your server now knows the caller's name, and still doesn't store a single user.

## The token is doing the work

```py
headers={"Authorization": f"Bearer {auth_info.token}"}
```

You're a client now. For one request, EpicMe stops being the server holding a
token and becomes the caller presenting one — the same header, the same scheme,
pointed the other way. The authorization server does to you exactly what you do
to your own callers: reads the token, works out whose it is, answers accordingly.

Which is why there's no user id in that request. There's nowhere to put one. The
token *is* the question — "who is this?" — and the profile that comes back is the
only profile that token could ever produce. You cannot fetch Olivia's profile
with Kody's token; not because you're careful, but because the request has no
parameter for making that mistake.

Look at what the authorization server does with it:

```py
access = await provider.load_access_token(token)
if access is None:
    return JSONResponse({"error": "invalid_token"}, status_code=401, ...)
if "user:read" not in access.scopes:
    return JSONResponse({"error": "insufficient_scope"}, status_code=403, ...)
user = USERS.get(access.subject or "")
```

`access.subject` — the server derives the user from the token, never from the
request body. That's the same instinct you just built into `server.py`, seen from
the other side. Both servers get identity from the credential; neither takes it
from input.

That 403 on `user:read` is a preview. Your tokens carry that scope, so it never
trips. The next topic is what happens when they don't.

## Non-200 means None

```py
if response.status_code != 200:
    return None
```

Same shape as `resolve_auth_info`. The token expired between your introspection
call and this one, the authorization server is down, the scope isn't there — all
of it collapses to "no profile", and `whoami` turns that into a sentence a model
can read:

```py
raise ValueError("Could not load your profile from the authorization server")
```

The alternative is `response.json()["username"]` throwing a `KeyError` on the 403
body — which tells the model nothing and buries the real problem in a stack
trace. Errors from another service become errors of yours; decide their shape at
the boundary.

## Two sources, two questions

You now pull identity from two places, and it's worth naming the split:

- **Introspection** (`03.auth-info`) — is this token real, whose is it, what can
  it do. Answers a security question. Runs on every single request, at the door.
- **Userinfo** (this step) — what is this person's name and email. Answers a
  display question. Runs only when a tool actually needs a profile.

`whoami` shows both halves in one payload: `user.username` and `user.email` came
from userinfo, `auth_info.client_id` and `auth_info.scopes` came from
introspection at the front door. Different questions, different endpoints, one
token.

## Topic done

You started this topic with a server that authenticated people and then handed
everyone Kody's journal. Now the caller travels from the middleware to your tools
in a ContextVar, every database call is scoped to their id, one user provably
cannot read another's entry even holding its id, and when a tool needs a name it
asks the server that owns names, using that user's own token.

The remaining question is the one the 403 above hinted at. Kody is Kody, and
that's settled — but a token isn't only *who*. It's also *what they're allowed to
do*. That's scopes.
