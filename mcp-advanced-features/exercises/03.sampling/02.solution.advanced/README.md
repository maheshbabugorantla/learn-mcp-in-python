# Tags the model picks

The call is the same one you already know; what changed is what you did with the
answer. You asked for structure, parsed the free text into a list of names, and
ran each name through find-or-create before attaching it. The model's sentence
became rows in the database.

Two details carried the weight. Parsing defensively — split, strip, drop empties —
means a sloppy reply degrades to a shorter list instead of an error. And
find-or-create means a suggested name that already exists (`"work"` from the seed)
is reused rather than re-created, so the unique-name constraint is never touched.

This is sampling as a real building block: the server treats the client's model as
a helper it can call inline, gets back natural language, and turns it into
concrete work — all inside a single tool call the caller never had to orchestrate.
