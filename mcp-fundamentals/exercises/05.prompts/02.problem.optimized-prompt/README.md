# A prompt that carries its own data

Your job: stop asking the model to go fetch things, and send the data with the
prompt instead.

## The problem with what you built

Your prompt says, in effect: *go read entry 3, then go read the tag list, then
think about it.* That means two round trips before any real work starts, and the
model has to guess the right URIs. If it guesses wrong, it fails at a task you
already knew how to do.

But look at your server. You have `db`. You can just... look the entry up
yourself.

```py
entry = db.get_entry(int(entry_id))
tags = [tag.to_dict() for tag in db.get_tags()]
```

You know the id. You know where the tags live. Making the model rediscover that
is asking it to guess at something you already have in a variable.

## Messages can carry more than text

A message's `content` doesn't have to be text. An `EmbeddedResource` carries a
payload *plus the URI it came from* — and you've met it before. It's exactly what
your `get_entry` tool hands back. The helper is already sitting in `server.py`:

```py
def _embed(uri: str, payload: object) -> EmbeddedResource:
    ...
```

That's the part worth pausing on. The same `EmbeddedResource` you returned from a
*tool* in the last topic drops straight into a *prompt message* here, unchanged.
The primitives compose; you're not learning a new mechanism, just a new place to
put one you already have.

The URI is the part that's easy to undervalue. You could paste the JSON into the
text and the model would read it. But then it's just characters in a wall of
prose. Embedded with `epicme://entries/3` attached, it's *the entry*, addressable
and re-readable — the model can tell the difference between the entry and the tag
list without you explaining which is which.

To send several, return a list of messages instead of a string:

```py
def suggest_tags(entry_id: str) -> list[base.Message]:
    return [
        base.UserMessage("...instructions..."),
        base.UserMessage(_embed(f"epicme://entries/{entry.id}", entry.to_dict())),
        base.UserMessage(_embed("epicme://tags", tags)),
    ]
```

## Say what should happen next

While you're here, make the instructions do real work. The model can create tags
(`create_tag`) and attach them (`add_tag_to_entry`) — say so, and say that you
want to approve the suggestions first. A prompt is where your expertise about
*how to do this task well* gets to live.

## One new failure mode

Fetching in the prompt means the prompt can now fail: someone will ask for entry
999. Raise a `ValueError` when it isn't there. The client gets a clean error
instead of a confusing conversation about an entry that doesn't exist.

## Your task

Open `server.py` and follow the TODO. Then:

```sh
uv run pytest exercises/05.prompts/02.problem.optimized-prompt
```

Stuck? Diff against `exercises/05.prompts/02.solution.optimized-prompt/server.py`.

## What’s next?

Next you will complete the prompt's `entry_id` argument. The final step connects
the same server-wide completion dispatcher to a user-facing prompt, so a person
can choose valid context without memorizing database ids.
