# The user

You know who's calling. Your server takes a token, hands it to the authorization
server, and gets back a verified user id. That's real work, and so far it has
bought you nothing at all.

Look at what your tools still do:

```py
user_id = DEFAULT_USER_ID
entry = db.get_entry(user_id, id)
```

Everyone who connects gets Kody's journal. Olivia logs in as Olivia, proves it,
and reads Kody's diary. The server authenticates people and then ignores who they
are — which is worse than not authenticating at all, because now there's a login
screen making a promise the code doesn't keep.

The gap is structural, not lazy. Your `authorize` function has the caller and
lives at the front door. Your tools need the caller and live several frames
below, called by the MCP SDK, which has never heard of your middleware. Nobody
hands a tool the request. So this topic is about two questions: how does the
caller get from the door to the code that does the work, and how do you make it
impossible for that code to serve the wrong person?

There are two users in this course, `kody` and `olivia`, and they exist for one
reason: so you can prove one can't read the other's journal. A test that only
ever logs in as one person proves nothing about isolation. Two people, one
database, one entry id — that's the test that means something.

Two steps:

1. **token** — carry the authenticated user from the middleware into your tools
   with a `ContextVar`, and scope every database call to their id.
2. **user** — introspection gave you an id, not a name. Ask the authorization
   server for the profile, using the user's own token.

Run each exercise's tests from the `mcp-auth` directory, one directory at a time:

```sh
uv run pytest exercises/04.user/01.problem.token
```

No server to start — the tests run your app, and the authorization server, in
process.
