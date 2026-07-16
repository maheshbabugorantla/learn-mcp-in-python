# Introducing yourself

This is the hinge.

A client shows up knowing exactly one thing: your URL. Somebody typed it into a
config, or pasted it into a chat app. It doesn't know who issues tokens for you.
It doesn't know the authorization server exists. It has your URL and nothing
else.

The document you're about to write is how it finds out. **RFC 9728** — protected
resource metadata — is the answer to *"I've heard of you; who vouches for you?"*
Everything else in the chain follows from it: this is what the 401 will point at,
and what tells the client which authorization server to go read. Get this wrong
and no client ever finds its way in.

It's two keys.

```json
{
  "resource": "http://localhost:8788/mcp",
  "authorization_servers": ["http://localhost:7788"]
}
```

`resource` is which thing this document is about. `authorization_servers` is who
to go talk to about getting in. That's it — that's the whole introduction.

## Build the URL, don't type it

`resource` is your own MCP endpoint's URL, and there's an obvious way to produce
it that you should not use: typing it in. A hardcoded `http://localhost:8788/mcp`
works on your laptop and is wrong in every other place the code will ever run.

Take it from the request instead. The client just told you what host it reached
you on — use that:

```py
str(request.url.replace(path="/mcp", query=""))
```

Same code, right answer on localhost, right answer in production, right answer
behind whatever hostname someone deploys this under. The test pins the exact
string, so a hardcoded host fails loudly rather than in staging.

Note the path this gets served at: `/.well-known/oauth-protected-resource/mcp`,
with `/mcp` on the end. The document describes one specific resource, not the
whole host. A server could expose several, each with its own metadata and its own
answer about who guards it.

## What's not in it

No scopes. A client reading this learns *who* to authenticate with, not *what*
to ask permission for — that field shows up later, once there are scopes worth
naming.

And one thing to be sure of: this document must be readable by a client with **no
token**. That's not an oversight to fix later, it's the point. The only client
that needs these instructions is the one that hasn't got in yet. A login page you
have to be logged in to read is a locked door with the key inside.

## Your task

Two files again.

Open `auth.py` and write `handle_oauth_protected_resource_request`. Then open
`app.py`, import it, and add its `Route` at
`/.well-known/oauth-protected-resource/mcp`.

```sh
uv run pytest exercises/01.discovery/03.problem.pr
```

Stuck? Diff against `exercises/01.discovery/03.solution.pr/`.
