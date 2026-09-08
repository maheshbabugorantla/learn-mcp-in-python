# May they do this?

Every tool on your server starts the same way:

```py
auth_info = require_auth_info()
```

That line answers *who is this*. It has never once asked *and are they allowed*.
Right now a token with `entries:read` on it can call `create_entry`, because
nothing in your code has ever looked at `auth_info.scopes`. The consent screen
made Kody a promise; this is where you keep it.

## The list, and the type

Start in `auth.py` with the five scopes this server understands:

```py
SUPPORTED_SCOPES = [
    "user:read", "entries:read", "entries:write", "tags:read", "tags:write",
]

Scope = Literal["user:read", "entries:read", "entries:write", "tags:read", "tags:write"]
```

The `Literal` is worth a second. Scopes are strings, and strings are where typos
go to hide. Write `require_scope("entries:writes")` with a plain `str` and you get
a permission that compiles, runs, and silently never matches — a tool nobody can
call, discovered in production. With `Scope`, it's a type error before you run
anything.

## Every, not any

Then the check itself:

```py
def validate_scopes(auth_info: AuthInfo, scopes: list[Scope]) -> bool:
    """True if this token carries *every* one of `scopes`."""
    return all(scope in auth_info.scopes for scope in scopes)
```

`all`, not `any`, and that's not a detail. This function answers "may they do
this specific thing?" — and `add_tag_to_entry` touches an entry *and* a tag, so it
needs `entries:write` and `tags:read`. Both. A token with one of them can do half
the job, and half of that job is not a thing you can do.

## Then use it

In `server.py`, wrap the two together:

```py
def require_scope(*scopes: Scope) -> AuthInfo:
    auth_info = require_auth_info()
    if not validate_scopes(auth_info, list(scopes)):
        raise ValueError(...)  # name the missing scope
    return auth_info
```

**Raise, don't return an HTTP error.** Nothing went wrong at the HTTP layer: the
request was well-formed, the token is real, the client is who it says it is. This
one tool wasn't allowed. FastMCP turns your exception into a tool error the model
reads — so if you name the missing scope, the model can tell the user *"this app
only has read access to your journal"* instead of "it didn't work". You met this
rule in the fundamentals course: the error message is the recovery instructions.
It didn't stop being true because the subject changed to permissions.

Then swap `require_auth_info()` for `require_scope(...)` at the top of each tool,
resource and prompt. The TODO in `server.py` lists all eleven.

## Why the check is inside the tool

The TypeScript version of this workshop registers tools per connection, so a user
without `tags:read` never *sees* `create_tag`. Python's FastMCP registers tools
once, at import time, on a module-level `mcp` object — there's no per-connection
registration to hook. So your tool list is the same for everyone here, and the
scope check happens when a tool is *called*.

You could filter per request in SDK v1.28, but only by reaching into
`mcp._mcp_server` and `mcp._tool_manager` — private attributes, one refactor from
breaking. Not worth teaching. Checking inside the tool is the public, idiomatic
route, and it's what most real servers do anyway. (SDK v2 adds middleware that
would make filtering clean.)

## Your task

Open `auth.py` and `server.py` and follow the TODOs. Then:

```sh
uv run pytest exercises/05.scopes/01.problem.check-scopes
```

Stuck? Diff against `exercises/05.scopes/01.solution.check-scopes/`.

## What's next?

Next you ask the same question at the front door. A per-function check answers
"may this token do *this*"; none of them answers "can this token do anything here
at all", which is the one a client with the wrong scopes actually needs.
