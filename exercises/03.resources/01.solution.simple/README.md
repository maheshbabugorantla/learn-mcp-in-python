# Simple Resource (solution)

`epicme://tags` is now a static resource. The decorator carries the URI, the
function does the lookup, and `mime_type="application/json"` tells the client
to treat the output as data rather than prose.

Worth noticing: the function takes no arguments. A static resource is one fixed
URI, so there's nothing to parse out of it — that changes in the next step.

The lesson is in [01.problem.simple](../01.problem.simple/README.md).
