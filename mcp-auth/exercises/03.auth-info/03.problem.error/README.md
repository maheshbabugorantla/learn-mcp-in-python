# Say why — when you know

Two clients get a 401 from your server. One never had a token. The other has one
that expired an hour ago. Both get this:

```
WWW-Authenticate: Bearer realm="EpicMe", resource_metadata="https://.../oauth-protected-resource/mcp"
```

Identical. But their problems aren't identical, and neither is the fix. The first
client needs to go get a token — read the metadata, register, send the user to
log in. The second already did all that; it has a refresh token in its pocket and
needs to know it should use it. Handing both the same sentence means one of them
does the wrong work.

## The auth param that names the problem

RFC 6750 has a field for exactly this:

```
error="invalid_token"
error_description="The access token is invalid or expired"
```

`error` is the machine-readable half — a client matches on `invalid_token` and
knows, without parsing English, that refreshing is the move. `error_description`
is for the human reading logs at 2am.

Note how little it says. *Invalid or expired* — not which. You spent the last
step making sure your server can't tell those apart, and this is the same
restraint on the way out: **a 401 never explains why a token failed.** The point
of the error code is to say what kind of problem the client has, not what kind of
token you were holding.

## Only when they sent something

Here's the condition that makes this exercise more than a copy-paste:

```py
had_a_token = "authorization" in request.headers
```

`error="invalid_token"` is a statement about a token. If the client didn't send
one, there is no token, and calling it invalid is false. Worse, it's actively
misleading — a client told its token is invalid will go try to refresh a token it
does not have, fail at that, and end up further from a working session than a
plain "you're not authenticated" would have left it.

So the rule: say the token is bad only when there was a token to be bad.

Both kinds of 401 still carry `resource_metadata`, though. Every rejection, no
matter the cause, points at the document that says how to get in. That's what
keeps a 401 a negotiation and not a dead end — a client whose refresh fails can
always fall back to reading the metadata and starting over.

## Your task

Open `auth.py` and follow the TODO in `handle_unauthorized`.

```sh
uv run pytest exercises/03.auth-info/03.problem.error
```

The tests check both directions: a bad token gets the error param, a missing
token doesn't, and both still get `resource_metadata`.

Stuck? Diff against `exercises/03.auth-info/03.solution.error/`.

## What's next?

Next, **The user** spends what introspection has been producing all along. Every
caller still gets the same journal today — the server works out exactly who is
asking, and then hands them somebody else's diary.
