# When the answer is no

Send your server a token it has never seen and it doesn't say no. It crashes:

```
ValidationError: 3 validation errors for ActiveToken
  client_id  Field required [input_value={'active': False}]
```

The authorization server did its job. It answered `200 {"active": false}` —
*that token means nothing to me*. Your model doesn't believe such an answer
exists, so it raises, and a routine bad token becomes a 500.

## One field, two shapes

An introspection response isn't one thing with optional bits. It's two genuinely
different documents, and `active` tells you which one you're holding:

```json
{ "active": true, "sub": "user-kody", "client_id": "test-client", "scope": "entries:read" }
{ "active": false }
```

That second one is the whole message. No `sub`, no expiry, no "expired" versus
"revoked" versus "never existed" — and that silence is the spec being careful.
All three of those are real, different situations, and RFC 7662 makes them look
identical on purpose. If a dead token said *expired* and a fake one said
*unknown*, anyone could sit on this endpoint and map out which tokens once
existed. So the endpoint says the same nothing to every one of them.

Your models should say that too.

## A union, not an if

The obvious fix is optional fields and a guard: `sub: str | None`, then check
before you touch it. Don't. That leaves `sub` readable on a dead token, and the
only thing stopping you reading it is remembering to check — every time, forever.

Model the two shapes as two types instead:

```py
class ActiveToken(BaseModel):
    active: Literal[True]
    client_id: str
    scope: str
    sub: str

class InactiveToken(BaseModel):
    active: Literal[False]
```

`InactiveToken` has one field, deliberately. There's nothing else to put on it.

Then join them with the field that tells them apart:

```py
IntrospectionResponse = Annotated[
    ActiveToken | InactiveToken, Field(discriminator="active")
]
```

A **discriminated union**. Pydantic reads `active`, picks the branch, and
validates against that shape alone. `{"active": false}` stops being a validation
error and becomes an `InactiveToken` — a normal value you can return from.

The payoff is what it makes impossible. After `if not data.active: return None`,
your type checker knows `data` is an `ActiveToken`, so `data.sub` is safe. Before
that line, `data` might be an `InactiveToken`, which *has no* `sub` — reading it is
an error your editor catches while you type. You can't forget the check, because
forgetting it doesn't compile.

(If you've done the TypeScript version of this workshop: pydantic is standing in
for Zod, and the shape maps over almost line for line. Discriminated unions are
the same idea in both.)

## Your task

Open `auth.py` and follow the two TODOs — rework the models into a discriminated
union, then handle the inactive branch in `resolve_auth_info`.

```sh
uv run pytest exercises/03.auth-info/02.problem.active
```

The tests send a token that was never issued, and revoke a good one mid-flight.
Both should come back 401, not 500.

Stuck? Diff against `exercises/03.auth-info/02.solution.active/`.

## What's next?

Next you give the 401 a reason. There's a wrinkle worth seeing coming: a reason
is only honest when the caller actually sent something, so the same handler has
to say different things depending on what arrived.
