# Say why — when you know

```py
had_a_token = "authorization" in request.headers
auth_params = [
    'Bearer realm="EpicMe"',
    *(
        [
            'error="invalid_token"',
            'error_description="The access token is invalid or expired"',
        ]
        if had_a_token
        else []
    ),
    f'resource_metadata="{resource_metadata_url(request)}"',
]
```

Now the two 401s read differently, and each one tells its client what to do next.

No header:

```
WWW-Authenticate: Bearer realm="EpicMe", resource_metadata="https://.../oauth-protected-resource/mcp"
```

*You're not authenticated. Here's where the instructions are.*

A token that didn't survive introspection:

```
WWW-Authenticate: Bearer realm="EpicMe", error="invalid_token",
  error_description="The access token is invalid or expired", resource_metadata="https://..."
```

*What you sent isn't good anymore. Refresh it — or if that fails, the
instructions are still right here.*

## The condition is the lesson

The spread-if is a little dense, but the thing it encodes is worth it. Dropping
`error="invalid_token"` onto every 401 is the version most people write, it passes
a test that only checks the bad-token case, and it's wrong in a way that only
shows up in someone else's client: told its token is invalid, it goes off to
refresh a token it never had.

Which points at something general about error responses. An error is a claim
about what happened, and a claim you can't support is worse than saying less.
`invalid_token` is only true if a token was sent. So it's only sent if a token
was.

## What you didn't say

Look at the description you shipped: *The access token is invalid or expired.*
Vague, and correct. You genuinely don't know which — the authorization server
told you `{"active": false}` and nothing more, and if you did know, you still
wouldn't say. Not knowing why is the design; you've now got it enforced from the
introspection endpoint's response all the way out to the header.

Meanwhile `resource_metadata` is on both, and stays on both forever. Whatever
went wrong, the way back in is the same document. That's what makes a 401 the
first line of a conversation instead of the end of one.

## Where you are

Your resource server now takes an opaque string, asks the authorization server
what it means, handles both answers it can get back, and rejects the bad ones with
a header the client can act on. `resolve_auth_info` returns an `AuthInfo` with a
`user_id`, a `client_id`, and a list of `scopes`.

You're authenticating. You're not yet authorizing — nothing has asked whether
this particular user may read this particular journal, or whether their token
carries the scope for what they're about to do. `AuthInfo` is where both of those
answers come from, and it's sitting there in `authorize`, currently thrown away
the moment it turns out not to be `None`.

That's the next two topics.
