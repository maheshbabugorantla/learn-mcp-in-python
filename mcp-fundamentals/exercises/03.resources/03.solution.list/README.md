# Listing Resources (solution)

`epicme://entries` is a plain static resource that indexes the journal, and it
exists because Python templates have no `list` callback — they only ever surface
under `resources/templates/list` as patterns.

So the two work as a pair: the collection answers "what exists?", the template
answers "give me that one." Each record carries its own `uri`, which is what
lets a client walk from the index to the contents without knowing how to build
an `epicme://` URI itself.

The index stays lean on purpose — id, title, uri. Whoever wants the rest can
follow the link.

The lesson is in [03.problem.list](../03.problem.list/README.md).
