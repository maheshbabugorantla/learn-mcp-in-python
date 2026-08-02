# Resources

In the last topic you gave the model tools — things it can *decide* to call. A
resource is the other half of the picture: something the *application* decides
to load.

That distinction is the whole point of this topic, so it's worth being precise:

- A **tool** is model-driven. You describe what it does, and the model chooses
  to call it, when it wants, with arguments it makes up. Calling a tool can
  change the world — create an entry, delete a tag, send an email.
- A **resource** is application-driven. It's a named piece of context sitting at
  a URI, waiting to be read. The client app decides what to load and when.
  Reading a resource should be a plain lookup with no side effects — think
  `GET`, not `POST`.

Concretely: a user in a chat client might click an attachment picker, see
"A quiet morning" listed, and attach it to their message. Nothing about that
flow involved the model deciding anything. The app listed some URIs, the user
picked one, the app read it, and the text landed in the conversation. That's a
resource.

Every resource has a **URI**, and you get to invent the scheme. Ours is
`epicme://`:

```
epicme://tags            a static resource — always the same URI
epicme://tags/{id}       a resource template — a family of URIs
```

A **static resource** lives at one fixed URI. A **resource template** describes
a whole family of them with a placeholder, so `epicme://tags/1` and
`epicme://tags/2` are both served by one function.

Clients discover them through three requests, and knowing which is which will
save you a lot of confusion later:

- `resources/list` — the concrete URIs you can read right now
- `resources/templates/list` — the URI *patterns* you can fill in
- `resources/read` — give me the contents at this URI

Over the next four steps you'll build all of it: a static resource, two
templates, a collection resource that makes individual records discoverable,
and autocomplete for template placeholders.

The REST analogy is useful but incomplete. A resource resembles a `GET`-able
representation, and a URI template resembles a parameterized route. MCP adds a
control decision around that address: the application chooses when context is
loaded, while the model chooses when to invoke a tool. The exercises build the
discovery path from one fixed URI to a family of records that a client can
present to a person.

## What’s next?

After the four resource steps, **Resource Tools** puts the two control surfaces
in one reply: a tool performs the action and hands back the resource context it
already has, either inline or as a link the client can follow.
