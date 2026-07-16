# Ask what the token means

Your server can now tell you who's calling. Walk back through what that took.

## Parse before you dial

```py
scheme, _, token = auth_header.partition(" ")
if scheme.lower() != "bearer" or not token.strip():
    return None
```

The cheap checks come first, and not only for speed. `Authorization: Basic abc123`
is not a bearer token — sending its contents to an introspection endpoint is
asking a question about the wrong thing. `.lower()` is there because the scheme is
case-insensitive per RFC 7235 and real clients do send `bearer`.

## The question

```py
response = await get_http().post("/oauth/introspection", data={"token": token})
if response.status_code != 200:
    return None
```

`data=` rather than `json=` — introspection is form-encoded. The status check is
the one line that's easy to skip and shouldn't be: if the authorization server is
down or returns a 500, you have no idea whether the token is good, and **no idea
is not the same as yes.** Failing closed here means an outage locks people out.
Failing open means an outage lets everyone in.

## The parse, and the shape change

```py
data = _introspection_response.validate_python(response.json())

return AuthInfo(
    token=token,
    client_id=data.client_id,
    scopes=data.scope.split(),
    user_id=data.sub,
)
```

`TypeAdapter` gives you pydantic validation without wrapping the whole thing in a
model you'd never otherwise want. The response is checked once, at the boundary,
and everything downstream gets a typed object instead of a dict that might have
anything in it.

Notice the renames on the way through. `sub` becomes `user_id`. `scope` becomes
`scopes` and turns from `"entries:read tags:read"` into `["entries:read",
"tags:read"]`. That's not decoration. OAuth's vocabulary stops at this function;
the rest of your server reads `auth_info.user_id` and never learns that a spec
somewhere calls it "subject". The wire format is contained.

## And the guard finally guards

```py
auth_info = await resolve_auth_info(request.headers.get("authorization"))
if auth_info is None:
    return handle_unauthorized(request)
return None
```

Same two lines it always was. But "did you send a header" has become "does the
authorization server agree this token means something," and that's the difference
between a lock and a picture of a lock.

## What's still broken

Send a token that was never issued and your server doesn't 401. It 500s:

```
ValidationError: 3 validation errors for ActiveToken
  client_id  Field required [input_value={'active': False}]
  scope      Field required [input_value={'active': False}]
  sub        Field required [input_value={'active': False}]
```

Introspection answered perfectly well — `200 {"active": false}`, meaning *I don't
know that token*. Your model has no idea what to do with an answer that shape, so
it raises, and a crash becomes a 500.

The tests here pass because none of them send a bad token. That's not an
oversight; it's the seam. You built the happy path first and it works. Next step
teaches the model that "no" is a valid answer.
