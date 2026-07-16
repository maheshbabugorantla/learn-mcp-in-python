# Auth info

Your server now asks for a token. It just doesn't read it.

That's where the last topic left you: `/mcp` rejects anyone who arrives without
an `Authorization` header, and waves through anyone who arrives with one. The
word "Bearer" is the whole security model. Fixing that means answering a question
you have so far avoided — *what does this token actually say?*

Look at one and the problem is obvious:

```
Bearer 8xJ2mQvK3nR7pL1wY6tZ4cF9hB0sD5gA
```

Nothing. It says nothing. It's a random string, and that's not laziness on the
authorization server's part — it's the design. The token is a **claim check**, not
a document. There's no user in there, no expiry, no list of permissions, because
there's nothing in there at all. The facts live back at the authorization server,
in a dictionary, next to the string that points at them.

So the only way to learn what a token means is to go ask the server that issued
it. That question has a name and an RFC:
[**introspection**](https://datatracker.ietf.org/doc/html/rfc7662). You POST the
token, and you get back the three things worth knowing:

```json
{ "active": true, "sub": "user-kody", "client_id": "test-client", "scope": "entries:read tags:read" }
```

Read those as *who*, *what app*, and *allowed to do what*. `sub` is the person.
`client_id` is the software acting on their behalf. `scope` is the permissions
they agreed to hand over. Every access decision in the rest of this workshop is
made out of those three fields.

## The other way, and why not

You may know that JWTs exist and that they carry their claims inside the token,
signed. A resource server can verify one locally — no network call, no round trip
per request. That's a real advantage and it's why JWTs are everywhere.

The bill comes due at revocation. A signed token is valid because the math says
so, and the math doesn't know a user hit "log out" thirty seconds ago. You either
accept a window where dead tokens still work, or you start calling the
authorization server to check — which is the thing you were avoiding. Opaque
tokens pay the round trip up front and get instant revocation for it. Neither is
free. This workshop takes the opaque side, so introspection is the price.

Three steps:

1. **introspect** — write `resolve_auth_info`, which turns an `Authorization`
   header into an `AuthInfo`, and make `authorize` use it instead of trusting the
   header.
2. **active** — teach the model that `{"active": false}` is a real answer, and
   that a dead token has nothing else to say.
3. **error** — say *why* a 401 happened, but only when you actually know.

A note on the order. The upstream TypeScript workshop runs these as introspect →
error → active, which leaves a step where an invalid token crashes the server
with a 500 (their test asserts the 500). This port swaps the last two, so an
invalid token gets a clean 401 before you start polishing the words in it. Same
material, honest behavior at every step.

Worth having open: [RFC 7662](https://datatracker.ietf.org/doc/html/rfc7662) and
the [MCP authorization
spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization).

Run each exercise's tests from the `mcp-auth` directory, one directory at a time:

```sh
uv run pytest exercises/03.auth-info/01.problem.introspect
```

One at a time matters here — every exercise has its own `auth.py` and `app.py`,
and pytest can't import two modules with the same name at once. No server to
start; the tests run your app and the authorization server in process.
