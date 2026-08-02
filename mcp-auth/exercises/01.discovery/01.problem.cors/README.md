# Who's allowed to read this

A browser that can't read an error response can't tell you what went wrong.

That's the whole reason this exercise comes first. Some of the clients that will
talk to your server are web apps, running in a browser, on an origin that isn't
yours. When such a client asks for your discovery metadata, the browser checks
whether you said it's allowed to read the response — and if you didn't, the
browser doesn't hand the JavaScript a helpful message about CORS. It hands it
nothing. The request may well have succeeded. The developer sees a blank failure
and no clue why.

So before you serve any metadata, you decide who gets to read it.

## Not everything wants a browser

CORS headers are permission slips, and you don't hand out permission you don't
need. Two kinds of URL live on this server:

`/.well-known/...` is metadata. It's a public description of how to log in —
endpoint URLs, supported grant types, where to register. There's nothing secret
in it. It's *meant* to be read by anyone, and you can't know in advance which
origins will want to.

`/mcp` is the actual server. Clients talk to it over HTTP, but not from a
browser page on someone else's site. It has no business inviting arbitrary
origins to call it, so it gets no CORS headers at all.

That's the shape of the function you're writing: look at the URL, and either
return headers or return `None`.

```py
def get_cors_headers(request: Request) -> Mapping[str, str] | None:
    if "/.well-known" not in str(request.url):
        return None
    return { ... }
```

`Access-Control-Allow-Origin: *` is the right answer for the metadata, and it's
worth being clear about why that's not lazy. `*` is dangerous when it exposes
something a user's cookies could unlock. Here it exposes a document you'd happily
print on a billboard.

## The plumbing is done

`WithCors` in `utils.py` already wraps the whole app. It calls your function,
answers `OPTIONS` preflights itself with a 204, and copies whatever you return
onto the response. Read it — it's short, and it explains one thing that will
otherwise look broken.

The test asks for `/.well-known/oauth-authorization-server` and asserts your CORS
headers came back on a **404**. That's not a mistake. Nothing serves that path
yet; it arrives in the next exercise. But `WithCors` puts the headers on *every*
response, errors included, and that's exactly the point of the first paragraph.
A 404 a browser can read is a 404 you can debug.

## Your task

Open `app.py` and fill in `get_cors_headers`. Then:

```sh
uv run pytest exercises/01.discovery/01.problem.cors
```

Stuck? Diff against `exercises/01.discovery/01.solution.cors/`.

## What's next?

Next you serve the first of this topic's two documents — and it describes the
authorization server, not you. Your server's job there is mostly to know where to
forward the question.
