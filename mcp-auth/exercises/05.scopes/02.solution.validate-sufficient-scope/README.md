# Any and all

Your server now says no in two places, and they're saying two different things.

At the door, in `app.py`:

```py
if not has_sufficient_scope(auth_info):
    return handle_insufficient_scope()
```

Inside each tool, in `server.py`:

```py
auth_info = require_scope("entries:write")
```

Both read `auth_info.scopes`. One uses `any`, one uses `all`. That's not a
stylistic split — it's two genuinely different questions, and once you see it in
one API you'll see it in every one you touch afterwards.

**Is this request worth handling?** is `any`. One usable scope and there's a
conversation to have. Zero, and every tool would refuse, so refuse once here
instead of making the client discover it five times.

**Is this call allowed?** is `all`. `add_tag_to_entry` needs `entries:write` and
`tags:read`; both, or nothing. A token that has one of them still gets past the
door — it can do plenty of other things — and gets refused right here.

Neither check can do the other's job. The door doesn't know which tool is coming.
The tool doesn't get to hang up on the connection.

## Three ways to be turned away

Your server's front door now distinguishes three cases, and each one tells the
client something it can act on:

```
no token / bad token   -> 401, WWW-Authenticate names the metadata URL
valid, useless token   -> 403, WWW-Authenticate lists what would work
valid, useful token    -> in you come; the tools take it from here
```

The 401 says *go get a token*, and points at the document explaining how. The 403
says *not that token* and names the alternatives. Both refusals are directions.
Neither is a dead end — which has been the pattern since the first topic in this
course: an error is the last thing the other side hears from you, so make it the
thing that unblocks them.

## The status code is an instruction

It's easy to read status codes as labels — 401 means unauthorized, 403 means
forbidden, fine, whatever. They're not labels. They're branches in someone else's
code.

A client that gets a 401 refreshes its token and retries, because that is exactly
what 401 tells it to do. Send one to a client whose token is fine but useless and
it will refresh a perfectly good token, get the same token back, retry, get 401,
refresh. Forever. Nothing is broken anywhere in that loop except your choice of
number.

The 403 breaks it. *This token will never work here.* Now the client can do the
only useful thing available: go get a different one, asking for scopes that
actually exist — which, conveniently, your `error_description` just listed for it.

Which raises the obvious question. Why is the client guessing at scopes at all?
It should have known which ones to ask for before it ever sent Kody to log in.
That's the next step.
