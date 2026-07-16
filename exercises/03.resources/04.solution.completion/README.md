# Completions (solution)

One `@mcp.completion()` handler now covers the whole server, which is why it
reads as a funnel: check it's a `ResourceTemplateReference` for the `id`
argument, dispatch on `ref.uri` to pick the right table, filter by
`argument.value`, and return `None` for everything else. That last part isn't
politeness — the handler is asked about every completable argument on the
server, so declining is most of its job.

`hasMore=False` says this is the complete set. If you were paging through
thousands of ids you'd return a slice and set it `True`.

The lesson is in [04.problem.completion](../04.problem.completion/README.md).
