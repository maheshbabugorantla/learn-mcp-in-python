# Don't make them guess

Put yourself in the client's shoes. It's never seen your server. It gets a 401,
follows `resource_metadata` to your protected resource document, reads which
authorization server to talk to, registers itself, and is about to send Kody off
to log in. It builds the authorize URL, and it needs to fill in one more
parameter:

```
scope=???
```

Your metadata never told it. So it guesses, and there are only two ways to guess.

**Ask for everything.** Now the consent screen shows Kody all five scopes for an
app that wanted to summarize his entries, and Kody clicks yes, because what else
is he going to do? He just granted write access to his journal to something that
only ever needed to read it. Every scope you made him approve unnecessarily is
one an attacker gets for free if that client is ever compromised.

**Ask for something plausible.** `read`. `journal`. `entries`. Your authorization
server has never heard of any of them. Best case it fails immediately; worse, it
issues a token carrying nothing you understand, and Kody finds out the app is
broken *after* logging in.

Neither of those is the client's fault. You had the list the whole time.

## One line

You already know the five, from step 1:

```py
SUPPORTED_SCOPES = [
    "user:read", "entries:read", "entries:write", "tags:read", "tags:write",
]
```

They belong in the protected resource metadata you built back in
`01.discovery/03.problem.pr` — the document that already says what this resource
is and who vouches for it. Add what to ask for:

```py
"scopes_supported": SUPPORTED_SCOPES,
```

That's the whole exercise. It's one key in a dict, and it's what turns your
discovery documents from *here's where to log in* into *here's how to log in
correctly on the first try*.

## Who reads this

Two audiences, and the second one matters more than it looks.

The client reads `scopes_supported` and now puts real strings in `scope=` —
ideally only the ones it needs, since it can see the menu and pick from it.

Then the consent screen in `src/epicme/auth_server.py` renders exactly those
scopes, as a list, to a person. Kody. He reads `entries:read`, `tags:read`, and
decides. That screen is the entire point of every string in this topic: a human
being, looking at a short honest list of what an app is asking for, choosing.
Everything you've built for three steps exists so that the list he sees is short
and true.

## Your task

Open `auth.py` and follow the TODO. Then:

```sh
uv run pytest exercises/05.scopes/03.problem.scope-hints
```

Stuck? Diff against `exercises/05.scopes/03.solution.scope-hints/`.

## What's next?

That's the last exercise. Read [`exercises/05.scopes/FINISHED.md`](../FINISHED.md)
— it recaps what you built by hand and then shows you the SDK settings that do
most of it for you, which is the right order to meet them in.
