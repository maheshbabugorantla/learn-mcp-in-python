# Discovery

Your MCP server holds the journal. It does not hold the users, and it does not
issue the tokens. Something else does that.

That split has a name. Your server is the **resource server** — it has the
entries, the tags, the thing worth protecting. The **authorization server** has
the accounts, the login screen, and the power to hand out tokens. They are two
different processes at two different URLs, and everything in this topic exists
because of that.

Sit with why. If one process did both jobs, none of this would be necessary. A
request would come in, the code would look up the session in a variable, and
that would be the end of it. But the token in front of you was minted by a
program you don't share memory with. You can't look it up in a variable. You
have to go ask — and before you can ask, everyone involved has to *find each
other*. That's discovery.

## The chain

Here's where you're headed. A client that has never heard of you, given nothing
but your URL:

1. It calls `/mcp` with no token. It gets a **401** back — but a useful one,
   pointing at your protected resource metadata.
2. That metadata says: *here's what I am, and here's the authorization server
   that vouches for me.*
3. The client reads the **authorization server's** metadata to learn where to
   register, where to send the user, where to get a token.
4. It registers itself, sends the user off to log in, and comes back holding a
   token.

Read that list again and notice what's missing: a human. Nobody pastes a client
ID into a config file. Nobody emails anyone an API key. Every link in that chain
is a document a machine reads at runtime, which is why each one has an RFC
behind it — **RFC 8414** for the authorization server's metadata, **RFC 9728**
for the protected resource's. MCP wires them together in its
[authorization spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization).

This topic builds links 2 and 3 — the documents. The 401 that kicks the whole
thing off comes later; for now `/mcp` stays wide open, and nothing is checking
who anyone is.

## Three steps

1. **cors** — decide which requests a browser is allowed to read, and which get
   nothing. Discovery documents are public; your MCP endpoint isn't browser
   business at all.
2. **as** — serve the authorization server's metadata, so a client looking for
   it on your host finds it.
3. **pr** — describe *yourself*: what this resource is, and who issues tokens
   for it. This is the hinge the rest of the course hangs on.

Run each exercise's tests from the `mcp-auth/` directory, one directory at a
time:

```sh
uv run pytest exercises/01.discovery/01.problem.cors
```

One at a time matters — pointing pytest at two exercise directories at once
makes it trip over the two identically-named `test_app.py` modules. No server
needs to be running. The authorization server starts up inside the test process.
