# One line to close the loop

Registering the tool was already done for you; the missing half was telling the
client:

```py
mcp.add_tool(beta_ping, name="beta_ping", description="A beta tool. Returns pong.")
await ctx.session.send_tool_list_changed()
```

That's the whole shape of a list-changed notification — do the thing, then
announce it. The `add_tool` line changes what the server *can* do; the
`send_tool_list_changed()` line changes what the client *knows*. Without the
second, `beta_ping` is a tool nobody thinks to call: reachable, invisible.

Notice the notification carries no payload about *what* changed — just "the list
is different." The client's response is to re-fetch `tools/list` and diff for
itself, which is exactly what the test does when it checks that `beta_ping` shows
up afterward.
