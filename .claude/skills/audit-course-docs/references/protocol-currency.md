# Protocol currency

Read this when auditing lesson prose for claims about how MCP behaves.

`exercise-auditor`'s other checks compare prose against the code in this
repository. This one compares prose against the **protocol**, which is a
different question with a different answer. While the courses still pin an
older SDK, prose can match the code perfectly and still teach something the
specification has removed. Neither check finds what the other does.

## This file is a cache, not the source of truth

Everything below was transcribed by hand from the specification. It exists so
an audit does not need ten web fetches, and it will drift. When it disagrees
with the sources below, **the specification is right and this file is a bug** —
fix it in the same pass, and say so in your findings.

Current revision: **2026-07-28**.

### Sources

Ordered by how much weight to give them in a disagreement.

| Source | Best for |
|---|---|
| [`schema.ts` for the revision](https://github.com/modelcontextprotocol/specification/blob/main/schema/2026-07-28/schema.ts) | Whether a type exists at all. The spec calls this authoritative. |
| [Deprecated features registry](https://modelcontextprotocol.io/specification/2026-07-28/deprecated) | What is currently deprecated. Authoritative and maintained; prefer it over the list below. |
| [Revision changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) | What changed and why, with the SEP behind each change. |
| [Specification index](https://modelcontextprotocol.io/specification/2026-07-28) | Prose requirements, MUST/SHOULD wording. |
| [Feature lifecycle policy](https://modelcontextprotocol.io/community/feature-lifecycle) | What Deprecated obliges, and the twelve-month window. |
| [Python SDK migration guide](https://py.sdk.modelcontextprotocol.io/migration/) | The 1.x to 2.x renames in the last section. |
| [MCP Apps extension](https://modelcontextprotocol.io/extensions/apps/overview) and [ext-apps](https://github.com/modelcontextprotocol/ext-apps) | Anything mcp-ui teaches. Versions on its own revision. |

A caution learned here: prose summaries of the SDK, including its own release
notes, have been wrong about what is *exported*. For an SDK claim, read the
installed package at the pinned version, not `main` and not a summary.

### Checking whether this file is current

[`/specification/latest`](https://modelcontextprotocol.io/specification/latest)
redirects to the current revision. If that is no longer 2026-07-28, everything
below is suspect: refresh it against the changelog for the new revision before
auditing, and update the revision line above.

Also compare against what the repo actually pins. If the courses have moved to
an SDK that implements a different revision, this file and the courses are out
of step, and that mismatch is itself a finding worth reporting.

## How to judge a claim

Three outcomes, and the distinction matters more than the list below:

- **Teaching it as current behaviour** is a finding. "The server speaks
  first", "call `ping` to check the connection".
- **Naming it as history or as deprecated** is correct and not a finding.
  "Sampling is deprecated; integrate with an LLM provider directly instead."
  The courses are expected to say this.
- **Prose that matches the pinned SDK but not the revision** is still a
  finding, reported under Spec currency rather than as an accuracy defect.
  It is not wrong about the code; it is wrong about MCP.

Report these under their own heading, **Spec currency**, separate from
accuracy defects. They are usually not fixable in the same pass, because the
replacement lesson may not exist yet, and a pointer to a lesson that has not
been written fails the verify-the-promise rule.

## Removed in 2026-07-28

Prose may not present any of these as something a server or client does.
Confirm against
[`schema.ts`](https://github.com/modelcontextprotocol/specification/blob/main/schema/2026-07-28/schema.ts)
when a call is close: a type that is absent from the schema does not exist.

| Gone | What replaced it |
|---|---|
| `initialize` / `notifications/initialized` handshake | Per-request `_meta`: `protocolVersion`, `clientCapabilities`, `clientInfo` |
| Protocol-level sessions, `Mcp-Session-Id` | Server-minted handles passed as ordinary tool arguments |
| `ping` | `server/discover`, which servers MUST implement |
| `logging/setLevel` | Per-request `_meta` `logLevel` |
| `resources/subscribe`, `resources/unsubscribe`, the HTTP GET endpoint | `subscriptions/listen`, with explicit opt-in types |
| `tasks/list`, blocking `tasks/result` | `tasks/get` polling and `tasks/update`, in the tasks extension |
| `notifications/elicitation/complete`, `elicitationId` | Client retries the original request; correlate via `requestState` |
| `notifications/roots/list_changed` | Roots is deprecated outright |
| SSE resumability: `Last-Event-ID`, event IDs | Nothing. A broken stream loses the request; reissue with a new id |

## Deprecated in 2026-07-28

The [deprecated features registry](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)
is the maintained list. Check it rather than trusting this snapshot, which
only covers what was deprecated as of the revision above and will not grow
when something else is.

Deprecated features stay functional for a minimum twelve-month window. Prose
may describe them as deprecated and give their migration; it may not build an
exercise on them or offer them as a reason to take the course.

- **Sampling.** Integrate with an LLM provider's API directly.
- **Roots.** Pass directories via tool parameters, resource URIs, or server
  configuration.
- **Logging.** Log to `stderr` on stdio, or use OpenTelemetry.
- **Dynamic Client Registration.** Client ID Metadata Documents are
  preferred; DCR remains for authorization servers that lack support.
- **HTTP+SSE transport.** Streamable HTTP.
- **`includeContext` values `"thisServer"` and `"allServers"`.** Omit the
  field, or use `"none"`.

## Reframed, not removed

The trap here is prose that is individually accurate and framed wrongly.

- **Servers no longer initiate.** `roots/list`, `sampling/createMessage` and
  `elicitation/create` as server-initiated requests are replaced by Multi
  Round-Trip Requests: the server returns `InputRequiredResult` with
  `resultType: "input_required"`, and the client retries the original request
  carrying `inputResponses`. Any sentence resting on "the server starts the
  conversation" is a finding even when every noun in it is real.
- **Elicitation survives, its mechanism does not.** It is an MRTR flow now.
- **MCP-UI is the MCP Apps extension**, on its own revision. MCP-UI persists
  as a client-side rendering library, not the server-side spec.
- **Results carry a required `resultType`.** Clients treat a missing one from
  an older server as `"complete"`.
- **List and read results require `ttlMs` and `cacheScope`.**
- **Resource-not-found moved from `-32002` to `-32602`.**

## SDK names that prose still uses

The courses move from `mcp` 1.x to 2.x. Prose naming the old API is a
finding once the course it appears in has been ported.

`FastMCP` is `MCPServer`. `mcp.server.fastmcp` raises on import in 2.x.
`isError`, `mimeType`, `inputSchema`, `outputSchema`, `structuredContent`,
`nextCursor`, `progressToken` are snake_case. `McpError` is `MCPError`.
`create_connected_server_and_client_session` is gone; the courses use
`Client` directly.
