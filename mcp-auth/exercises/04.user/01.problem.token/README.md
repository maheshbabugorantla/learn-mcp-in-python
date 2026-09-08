# Getting the caller to the code

Your job: make every tool serve the journal of whoever sent the token.

## The problem is a plumbing problem

`authorize` in `app.py` has the caller. It resolved the token, it holds an
`AuthInfo` with a `user_id` on it, and then it throws it away and returns `None`.
Meanwhile every tool in `server.py` starts like this:

```py
user_id = DEFAULT_USER_ID
```

A tool is a plain function. The MCP SDK calls it with the arguments the model
supplied and nothing else — no request, no headers, no session. It has no way to
ask who's calling.

## Not a tool argument

The obvious fix is a parameter: `def get_entry(user_id: str, id: int)`. Don't.

The *model* fills in tool arguments. It reads your schema and writes JSON. Add
`user_id` to the schema and you have handed your entire security model to a text
generator — one that is improvising, and that will happily write
`{"user_id": "user-olivia"}` because a sentence in the conversation mentioned
Olivia. The authenticated user must come from the token, on a path the model
cannot reach.

## A ContextVar is the path

A `ContextVar` is how Python hands something to code it isn't calling directly.
Set it at the front door; read it anywhere downstream in the same request.

```py
current_auth_info: ContextVar[AuthInfo | None] = ContextVar(
    "current_auth_info", default=None
)
```

Then `app.py` sets it once the token resolves, and any code running for that
request can read it — including a tool six frames down, called by a library that
has never heard of your middleware. If you've seen the Cloudflare version of this
workshop, this is `ctx.props`, minus the Cloudflare.

Pair it with a `require_auth_info() -> AuthInfo` that raises when there's nothing
there. It will never fire — `app.py` rejects tokenless requests first. It's there
for the day someone mounts the MCP app without the auth middleware: then the
server fails loudly instead of quietly serving a journal to nobody in particular.

## One detail that is load-bearing

`server.py` already has this:

```py
mcp = FastMCP(..., stateless_http=True, ...)
```

That's not a style choice. It makes the server handle each request in the task
that received it, which is what lets a ContextVar set by the middleware still be
readable inside the tool. Turn it off and every tool stops knowing who's calling.

## The database is on your side

Read the module docstring in `src/epicme/db.py`. Every method takes a `user_id`,
and there is no way to ask for "all entries" — only for *a user's* entries. The
unscoped query isn't discouraged, it's unwritable.

So `db.get_entry(user_id, id)` on someone else's entry returns `None`, exactly
like an entry that was never written. "Not yours" and "not there" come back
identical, on purpose: they're the same fact as far as that caller is entitled to
know. Say "you're not allowed to read entry 4" and you've just confirmed entry 4
exists.

(Upstream's journal lives on the auth server and is reached over HTTP, so their
version of this step is "pass the token to the DB client". Here the journal is
local sqlite and the step is "scope every query by the authenticated user's id".
Same lesson, simpler plumbing.)

## Your task

Three files, in order:

1. `auth.py` — add `current_auth_info` and `require_auth_info`.
2. `app.py` — set it in `authorize`, once you have a non-`None` `auth_info`.
3. `server.py` — swap each `user_id = DEFAULT_USER_ID` for
   `auth_info = require_auth_info()` and pass `auth_info.user_id` to `db`.

```sh
uv run pytest exercises/04.user/01.problem.token
```

The test creates an entry as Kody and one as Olivia, then has Kody ask for
Olivia's entry by id. It has to fail.

Stuck? Diff against `exercises/04.user/01.solution.token/`.

## What's next?

Next you put a name to that id, which means one more call out — and a detail
worth pausing on when you get there: your server presents the *user's* token to
make it, not one of its own.
