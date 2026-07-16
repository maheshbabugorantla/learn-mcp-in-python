# You're done

You started with a journal that handed itself to anyone who asked. You now have a
remote MCP server that a stranger's AI client can discover, log into, and use —
where every row it returns belongs to the person holding the token.

Here's what you built:

- **Discovery.** Two metadata documents and the CORS headers that let a browser
  read them, so a client that has only ever heard of your server can find out who
  issues tokens for it.
- **A 401 that's instructions rather than a door slam** — `WWW-Authenticate` with
  a `resource_metadata` pointer, and an `error` param only when there was
  actually a token to be wrong about.
- **Introspection.** Turning an opaque random string into a user id, a client id,
  and a list of scopes, by asking the only thing that knows.
- **A caller your tools can see**, carried on a ContextVar, with every database
  query scoped to their id — so "not yours" and "not there" give the same answer.
- **Scopes**, checked in two places for two different questions: can this token do
  *anything* here (403 at the door), and may it do *this* (a tool error the model
  can read).

The thread running through all of it: **your server is not the authority on who
anyone is.** It holds a journal. Somebody else holds the users. Every awkward
round trip in this course — the metadata, the introspection call, the userinfo
fetch — exists because those are two different things, and keeping them separate
is what lets a client you've never heard of use a server you wrote.

## The part where you find out the SDK does this

Now that you know what the machinery is, here's the shortcut.

The Python SDK ships a resource-server implementation. Hand `FastMCP` an
`AuthSettings` and a `TokenVerifier` and it will generate the protected resource
metadata, return the 401 with the right `WWW-Authenticate` header, and enforce
scopes — most of `auth.py` and `app.py`, gone:

```py
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings

class EpicMeVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        ...  # your introspection call — this part is still yours

mcp = FastMCP(
    name="epicme",
    token_verifier=EpicMeVerifier(),
    auth=AuthSettings(
        issuer_url="http://localhost:7788",
        resource_server_url="http://localhost:8788/mcp",
        required_scopes=["user:read"],
    ),
)
```

Inside a tool, `get_access_token()` from `mcp.server.auth.middleware.auth_context`
replaces the ContextVar you wired by hand — and it works the same way, for the
same reason.

This is not a bait and switch. Go read that code now and you'll recognize every
line of it, because you wrote those lines this week. That's the difference
between using a library and being stuck the first time it does something you
didn't expect. When a client fails against your server with a confusing 401, you
now know whether the bug is in the metadata, the header, the introspection, or
the scopes — and none of that is in the SDK docs.

## Where to go next

**Run it against a real client.** Two terminals:

```sh
uv run epicme-auth                                    # localhost:7788

cd exercises/05.scopes/03.solution.scope-hints
uv run uvicorn app:app --port 8788                    # localhost:8788
```

Point an MCP client at `http://localhost:8788/mcp`. It'll get your 401, read your
metadata, register itself, and send you to the consent screen — where you pick
kody or olivia and approve the scopes. Then ask it about your journal, and try it
again as the other user.

**Read the spec.** The [MCP authorization
spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
is short and will now read like a description of something you've met. The RFCs
underneath it are worth an afternoon: [8414](https://datatracker.ietf.org/doc/html/rfc8414)
(authorization server metadata), [9728](https://datatracker.ietf.org/doc/html/rfc9728)
(protected resource metadata), [7662](https://datatracker.ietf.org/doc/html/rfc7662)
(introspection), and [6749](https://datatracker.ietf.org/doc/html/rfc6749) itself.

**Then be honest about what this wasn't.** The EpicMe authorization server in
`src/epicme/` is a teaching prop: tokens in a dictionary, users with no
passwords, everything gone when the process exits. Real deployments hand that job
to something that already exists — an identity provider, or your app's existing
login. What you learned is the resource-server side, which is the side you
actually write. The parts this course skipped on purpose: token rotation and
refresh in anger, audience binding (RFC 8707 — note the `resource` field already
threaded through the provider), rate limiting, and what to do when the
authorization server is down and every introspection call is timing out.

Nice work. Go build something that knows who's asking.
