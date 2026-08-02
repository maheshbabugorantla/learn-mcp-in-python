# Who is this person?

Your job: turn a user id into a user.

## An id is not a name

Introspection told you `sub` is `user-kody`, and you put it in `AuthInfo.user_id`.
That's enough to scope a database query — it's the only thing you needed in the
last step — and it's useless for saying hello. A tool that wants to greet the
caller, or show their email, has an opaque string and nothing else.

That's not an oversight in the protocol. Look at who owns what. The authorization
server owns users: it has the password, the profile, the email. Your resource
server owns the journal. You have no `users` table, and you shouldn't — a copy of
someone's profile in your database is a copy that goes stale the day they change
their name.

So you don't look the user up. You ask the server that has them.

```py
response = await get_http().get(
    "/oauth/userinfo",
    headers={"Authorization": f"Bearer {auth_info.token}"},
)
```

## You present the user's token, not your own

This is the part worth slowing down for. You don't authenticate to the userinfo
endpoint as *the EpicMe server*, with some key of your own that lets you read any
profile you like. You send the token the user handed you.

That's why the request is safe to make. The authorization server looks at that
token, sees whose it is, and returns that person's profile and nobody else's. You
couldn't fetch Olivia's profile with Kody's token if you tried — there's no
parameter to try it with. Your server holding a master key would mean a bug in
your code could dump every user; holding the caller's token means the worst you
can do is ask about the caller.

This is the same pattern as any downstream API call made on behalf of a user, and
it's why the token is on `AuthInfo` at all. `user_id` is what you know about
them. `token` is what lets you go find out more.

## What to write

`fetch_user(auth_info) -> User | None`, in `auth.py`. GET `/oauth/userinfo` with
that header. Non-200 gives `None`; otherwise
`User.model_validate(response.json())`.

`None` on any non-200 keeps this consistent with `resolve_auth_info`: the token
was fine a moment ago and now it isn't, or the authorization server is having a
bad day, or the scopes don't cover this. The caller of `fetch_user` doesn't get a
taxonomy of failure, it gets "no profile", and the tool turns that into a clean
error.

The consumers are already written and already call it:

```py
@mcp.tool()
async def whoami() -> str:
    auth_info = require_auth_info()
    user = await fetch_user(auth_info)
```

`whoami` and the `epicme://user` resource both do exactly this — `require_auth_info()`
for the token you already have, `fetch_user` for the profile you don't. Same two
lines in both. Once `fetch_user` works, they work.

## Your task

Open `auth.py` and follow the TODO. Then:

```sh
uv run pytest exercises/04.user/02.problem.user
```

Four tests: `whoami` reports Kody, the same tool with Olivia's token reports
Olivia, the `epicme://user` resource reads, and `fetch_user` gets a profile back
from the authorization server directly.

Stuck? Diff against `exercises/04.user/02.solution.user/`.

## What's next?

Next, **Scopes** puts limits inside a token that is already valid. Right now
authenticating gets you everything: a client that asked for nothing but read
access to the journal can empty it.
