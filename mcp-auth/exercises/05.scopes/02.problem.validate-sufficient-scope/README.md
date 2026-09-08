# Turning away a token at the door

Someone connects with a valid token that carries `something:else` and nothing
else. It's a real token. The authorization server issued it. It belongs to a real
user. And it can't do one single thing on your server.

Right now that client gets in, initializes, lists your tools, calls one, and gets
a refusal. Calls another, gets a refusal. Your server says no five times, one tool
at a time, when it knew the answer before the first call.

Say it once, at the edge.

## A different question

Two of these are given to you in `auth.py`, because they're fiddly to describe and
easy to read:

```py
MINIMAL_VALID_SCOPE_COMBINATIONS: list[list[Scope]] = [
    ["user:read"], ["entries:read"], ["entries:write"], ["tags:read"], ["tags:write"],
]

def has_sufficient_scope(auth_info: AuthInfo) -> bool:
    return any(
        validate_scopes(auth_info, combination)
        for combination in MINIMAL_VALID_SCOPE_COMBINATIONS
    )
```

Look at that `any` next to the `all` you wrote last step, because this is the
heart of it. `validate_scopes` uses **all**: *may they do this specific thing?* —
and a thing needing two scopes needs both. `has_sufficient_scope` uses **any**:
*can this token do anything at all here?* — and one usable scope is enough to be
worth talking to. Same data, opposite operator, because they're not the same
question.

Each combination is the smallest set of scopes that buys you *something*. Ours are
all singletons, since any one of the five makes some part of the journal work. A
server whose cheapest useful operation needed two scopes together would list a
pair.

## 403, not 401

Your job is `handle_insufficient_scope()`, returning a **403** whose
`WWW-Authenticate` header carries `Bearer realm="EpicMe"`,
`error="insufficient_scope"`, and an `error_description` built from the
combinations.

The status code is the part to get right. A 401 means *go get a token* — and a
client that's told that will dutifully refresh, retry, get another 401, refresh
again. The authorization server behaves perfectly the whole time. The client
loops forever. A 403 means *that token will never work here; get a different one*.
That's the difference between a client that recovers and a client stuck in a
loop, and it's decided entirely by which number you type.

Build the description out of `MINIMAL_VALID_SCOPE_COMBINATIONS` — combinations
joined by commas, scopes within a combination joined by spaces — so the client is
told what *would* work rather than left to guess.

There is a `scope` auth param meant for exactly this, and you're not using it,
for a reason. It means "you need all of these". Here any one will do, and the spec
is clear that you shouldn't demand more than you need. Listing all five in `scope`
would tell a client that reads it correctly to go ask Kody for everything — which
is precisely the outcome scopes exist to prevent. So the explanation goes in
`error_description`.

## Then wire it up

In `app.py`, after you have the `auth_info` and before you set the ContextVar:

```py
if not has_sufficient_scope(auth_info):
    return handle_insufficient_scope()
```

Order matters. No usable token is a 401 (*who are you?*). A usable token that
can't do anything is a 403 (*not with that*). Don't confuse the two — the tests
check that a garbage token is still a 401.

## Your task

Open `auth.py` and `app.py` and follow the TODOs. Then:

```sh
uv run pytest exercises/05.scopes/02.problem.validate-sufficient-scope
```

Stuck? Diff against `exercises/05.scopes/02.solution.validate-sufficient-scope/`.

## What's next?

Next you close the loop this course opened. The protected-resource document you
wrote back in `01.discovery` is the first thing a client reads, and it has been
silent about scopes the whole time. One key fixes that.
