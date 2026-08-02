# Prompts

You've built tools and resources. Prompts are the third and last primitive, and
the easiest one to misunderstand — mostly because the name suggests something
vaguer than what it is.

The clearest way to hold all three apart is to ask **who decides**:

- A **tool** is what the *model* decides to call.
- A **resource** is what the *application* decides to load.
- A **prompt** is what a *person* picks from a menu.

A prompt is a template your server offers, and a human chooses deliberately. In
practice it shows up as a slash command, a menu item, or a button in the client's
UI. The user picks it, fills in any arguments, and your server hands back a
ready-made set of messages to start the conversation with.

So a prompt is really a piece of expertise you're packaging. You know how to ask
for good tag suggestions on a journal entry: what context to include, what rules
to state, which tools to mention. Your user shouldn't have to reinvent that
sentence. You write it once, they pick it from a list.

Three steps:

1. **prompts** — register a `suggest_tags` prompt with `@mcp.prompt()` and give
   it an argument.
2. **optimized-prompt** — stop asking the model to go fetch things. Send the
   entry and the tag list *inside* the prompt as embedded resources.
3. **completion** — let the client suggest valid values for the prompt's
   `entry_id` argument, so nobody has to memorize an id.

Run each exercise's tests from the repo root, one directory at a time:

```sh
uv run pytest exercises/05.prompts/01.problem.prompts
```

## What's next?

This completes the course's control model: the model chooses tools, the
application chooses resources, and the person chooses prompts. The final three
exercises show how those choices cooperate in one workflow rather than compete
as three unrelated APIs.
