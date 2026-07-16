# One line at the top of each function

That's what authorization turned out to be:

```py
auth_info = require_scope("entries:write", "tags:read")
```

Eleven functions, eleven of those, and your server now enforces what the consent
screen promised. Notice how little of your code changed. The tools are the same
tools, the database calls are the same calls. Authorization isn't a different kind
of MCP server — it's a question asked before the work starts.

## What the model actually sees

Call `create_entry` with a token that only has `entries:read`:

```
isError: True
"This requires the entries:write scope. This token has: entries:read."
```

Read that as a model would. It says what was needed, what's there, and by
implication why the two don't meet. A model handed that sentence can tell the
user *"this app has read-only access to your journal — you'd need to reconnect and
grant write access"*. A model handed `403` or `"forbidden"` can say "it didn't
work" and stop.

That's why this is a `raise` and not an HTTP status. HTTP is between the client
and your server, and at the HTTP layer nothing is wrong: real token, real user,
well-formed request. The refusal is about *this tool*, so it travels back the same
way any other tool refusal does — as a result the model reads.

## The two lines that are easy to skim past

```py
Scope = Literal["user:read", "entries:read", "entries:write", "tags:read", "tags:write"]
```

```py
return all(scope in auth_info.scopes for scope in scopes)
```

The first turns a whole class of bug into a type error. A misspelled scope with
`str` is a permission that never matches and never complains — the tool just
refuses everyone, forever, and the tests that pass are the ones checking it
refuses.

The second is `all` because the question is "may they do this specific thing?".
`add_tag_to_entry` needs `entries:write` and `tags:read`; a token with only one of
them gets turned away. Hold onto that word — the next step asks a question that
looks nearly identical and needs `any` instead, and the difference between the two
is the whole point of it.

## What you didn't build

Your tool list is identical for every caller. A read-only token still *sees*
`create_entry`; it just can't call it. That's a real difference from the
TypeScript workshop, where tools are registered per connection and a read-only
user never learns `create_entry` exists.

It's a difference worth being honest about rather than defending. Hiding a tool
is nicer: the model doesn't waste a call, and doesn't have to explain a refusal.
But in FastMCP v1.28 the registry is built once at import time on a module-level
server object, and filtering per request means poking at `mcp._mcp_server` and
`mcp._tool_manager` — private, undocumented, and a maintenance liability you'd
inherit forever. The public route is the one you took, and it's what most
production servers do regardless of language. SDK v2's middleware would make the
filtering version clean; when it lands, the check you wrote here still stands
behind it.

And it has to. Hiding a tool is a courtesy to the model. The check inside the tool
is the thing that actually stops a request.
