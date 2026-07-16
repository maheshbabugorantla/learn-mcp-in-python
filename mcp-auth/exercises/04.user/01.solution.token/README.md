# The journal belongs to whoever holds the token

Three small edits, and your server stopped lying. The login screen now means
something.

## The whole path, end to end

The front door resolves the caller and writes them down:

```py
auth_info = await resolve_auth_info(request.headers.get("authorization"))
if auth_info is None:
    return handle_unauthorized(request)

current_auth_info.set(auth_info)
```

A tool, several frames below, reads them back:

```py
auth_info = require_auth_info()
entry = db.get_entry(auth_info.user_id, id)
```

Nothing connects those two functions. `app.py` doesn't call `get_entry`; the MCP
SDK does, and it has never heard of your middleware. The ContextVar is the entire
link, and it works because `stateless_http=True` keeps the request in the task
that received it.

That's the shape worth keeping. Identity is established once, at the edge, in one
place you can read in ten seconds. Every tool below just asks. There's no auth
decorator on each function, no header parsing scattered through `server.py`, and
no way for a tool to be *accidentally* left out of the check — because a tool
that doesn't ask has no `user_id` to pass and doesn't compile past its first
`db` call.

## What the test proves

```py
stolen = call_tool(client, "get_entry", {"id": olivia_id}, token=token)
assert stolen.get("isError")
assert "not found" in tool_text(stolen).lower()
```

Kody knows the exact id of Olivia's entry — the test just read it out of her
`create_entry` result — sends a perfectly valid token, and gets *not found*.
Not "forbidden". Not "that's Olivia's". Not found.

That answer is a deliberate refusal to leak. `db.get_entry(user_id, id)` returns
`None` for someone else's row and `None` for a row that was never written, so the
tool cannot tell those apart, so it cannot tell the caller apart. Kody learns
nothing — not that the entry exists, not that Olivia has one, not how many there
are. The alternative, "403: that entry belongs to someone else", is a working
oracle for enumerating other people's data with nothing but a for-loop.

You didn't write that property in the tool. It falls out of `db.py`, where every
method takes a `user_id` and "all entries" isn't a question you can ask. Make the
unsafe query unwritable and the safe behavior stops depending on anyone
remembering.

## The guard that never fires

```py
def require_auth_info() -> AuthInfo:
    auth_info = current_auth_info.get()
    if auth_info is None:
        raise RuntimeError(
            "No auth info on this request — is the MCP app still wrapped in WithAuth?"
        )
    return auth_info
```

This raise is unreachable today. `app.py` 401s every tokenless request long
before a tool runs, so `current_auth_info` is always set by the time anyone
reads it.

Write it anyway. The dangerous version is `current_auth_info.get()` returning
`None` and some tool quietly passing that to `db` — a journal served to nobody in
particular, no error, no log line. The default is `None` because a ContextVar
needs one; `require_auth_info` is where you make sure `None` never travels any
further. It costs three lines and it converts a future silent data leak into a
stack trace on the first request.

## Where you are

Every operation is now scoped to the authenticated user, and the scoping isn't
optional. What you still don't know is anything *about* that user. Introspection
gave you `user-kody` — an id, not a name. The next step goes and asks.
