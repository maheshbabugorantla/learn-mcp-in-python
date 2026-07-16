# Resource Links (solution)

Your server now does both, and does them in the right places:

```
list_entries  → links     browse cheaply, contents stay put
get_entry     → embedded  they asked for this one, hand it over
create_entry  → embedded  it's brand new, and only the server knows the id
```

That's a working loop. The model lists, reads titles, picks entry 7, calls
`get_entry(7)`, gets the record. It paid for one entry to read one entry.

The `*(...)` unpacking in the content list is worth a second look — links are
just more items in the same list. Nothing special happens to them. The result is
a sequence of blocks, and you decide what kind each one is.

## What actually generalizes

Not "lists get links, singles get embeds." That's the answer for a journal, not
the rule. The rule is the question underneath it:

> Is the caller going to use this, or sort through it?

Use it → embed, and save the round-trip. Sort through it → link, and let them
pull what they want. When you're unsure, ask what fraction of the payload gets
read. High fraction, embed. Low fraction, link.

And notice these aren't different systems. `epicme://entries/1` is the same
resource whether it arrives embedded in a `create_entry` result, linked from
`list_entries`, or read straight off the template by a client that never called
a tool at all. The URI is the stable thing. Tools just choose how much of it to
send, and when.

The lesson is in [02.problem.linked](../02.problem.linked/README.md).
