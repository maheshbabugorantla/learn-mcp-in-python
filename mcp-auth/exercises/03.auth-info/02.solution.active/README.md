# When the answer is no

Two type declarations and one `if`, and a 500 became a 401.

## The union

```py
class ActiveToken(BaseModel):
    active: Literal[True]
    client_id: str
    scope: str
    sub: str


class InactiveToken(BaseModel):
    # Deliberately nothing else. A dead token tells you it's dead and no more.
    active: Literal[False]


IntrospectionResponse = Annotated[
    ActiveToken | InactiveToken, Field(discriminator="active")
]
```

`Literal[True]` and `Literal[False]` are what make this work. They're not
documentation — they're the values pydantic reads to decide which branch it's
looking at. Without the discriminator, pydantic would try each member in turn and
report a confusing pile of errors when both failed. With it, one field lookup
picks the shape, and a mismatch tells you exactly which branch was wrong.

## The line that ends it

```py
data = _introspection_response.validate_python(response.json())
if not data.active:
    return None
```

Everything before this line, `data` is either shape. Everything after, it's an
`ActiveToken` and nothing else — your type checker narrows it on that `if`, the
same way it narrows `x is None`. `data.sub` below is safe, provably, not by
convention.

That's the part worth keeping. The rule isn't "remember to check `active` before
reading `sub`." The rule is that `sub` doesn't exist on the branch where it would
be a lie, so there's no version of this code that reads it off a dead token.
Make the wrong thing unrepresentable and you stop needing the discipline.

## Three failures, one exit

The revocation test is the one to sit with:

```py
assert mcp_request(client, "initialize", INITIALIZE_PARAMS, token=token).status_code == 200

provider.access_tokens.pop(token)   # revoke it out from under the request

assert mcp_request(client, "initialize", INITIALIZE_PARAMS, token=token).status_code == 401
```

Same token, same string, one line apart. Valid, then not. That's the promise of
opaque tokens paying off: the authorization server deleted a dictionary entry and
your resource server knew immediately, because it asks every time. A signed JWT
would have sailed through that second request until it expired on its own.

And note where the revoked token, the never-issued token, and an expired one all
end up — the same `return None`, feeding the same 401. Your server doesn't know
which of the three it had, and doesn't want to. The authorization server refused
to say, `InactiveToken` has no room to record it, and `resolve_auth_info` has one
way to fail. The ignorance is designed at every layer.

## Still to do

Every 401 your server sends still says exactly the same thing. But "you sent
nothing" and "what you sent is stale" are different problems for the client to
solve, and right now it can't tell them apart. That's the last step.
