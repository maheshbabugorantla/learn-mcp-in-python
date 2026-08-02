# When a tool fails

Tools fail. The record isn't there, the API is down, the arguments are valid
integers that still make no sense together. So: what should your tool *do* about
it?

## Just raise

The answer is refreshingly boring. Raise a normal Python exception:

```py
if second_number < 0:
    raise ValueError("Second number cannot be negative")
```

No special error type, no result wrapper, no try/except at the call site. FastMCP
catches anything your tool raises and turns it into a normal MCP response marked
as an error. The server stays up and keeps serving. Every other client stays
connected. Only that one call fails.

That last part is the whole point. Your tool runs inside a long-lived server, on
behalf of a model that is often improvising its arguments. Bad calls aren't the
exception — they're Tuesday. A protocol where one bad call takes down the process
would be unusable, so MCP treats tool failure as a normal, expected response.

## The error is a message to the model

Here's what actually goes back to the client:

```py
result.isError        # True
result.content[0].text  # "Error executing tool add: Second number cannot be negative"
```

Notice your message survived the trip. That matters more than it looks.

There are two ways a model can learn something went wrong. One is a stack trace,
or a bare "500", or silence — from which it learns nothing and either gives up or
retries the same broken call. The other is a sentence: *the second number cannot
be negative*. That, a model can act on. It can flip the argument order, or ask
the user for a different number, or explain the constraint back to them. **The
error message is the recovery instructions.**

So write it like you're talking to whoever has to fix it, because you are.
"Second number cannot be negative" tells the model exactly which argument is
wrong and exactly what rule it broke. "Invalid input" tells it nothing.

## Rules that types can't express

`second_number: int` already stops `"banana"` — pydantic rejects it before your
function runs. But it can't stop `-5`, because `-5` is a perfectly good integer.

That's the split worth internalizing. The schema handles *shape*. Your function
body handles *meaning*: relationships between arguments, whether a record exists,
whether the caller is allowed. Validation you can express in the type, put in the
type. Everything else is a raise.

(EpicMe's rule here — no negative second number — is arbitrary. Real tools have
real ones. The mechanics are identical.)

## Your job

Open `server.py` and reject a negative `second_number`. Then:

```sh
uv run pytest exercises/02.tools/03.problem.errors
```

The tests check both paths: a good call still returns the sum, and a bad one
comes back as a readable error.

## What's next?

Next, the model needs context that is not an action. **Resources** introduces
application-controlled, addressable data so a client can load journal content
without asking the model to turn every read into a tool call.
