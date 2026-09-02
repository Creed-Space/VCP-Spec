# VCP Context Data Flow

<!-- vcp-document-control
status: Current companion
normative-authority: Accepted specifications and schemas
protocol-version: VCP 3.1
last-reviewed: 2026-08-13 status and authority classification
owner: VCP Spec maintainers
evidence-boundary: Architecture guidance only
-->

| Field | Value |
|:---|:---|
| Status | Current non-normative architecture companion |
| Normative authority | VCP 3.1 specifications, accepted VEPs, and schemas |
| Protocol baseline | VCP 3.1 |
| Last reviewed | 2026-08-13 |
| Owner | VCP Spec maintainers |
| Evidence boundary | Data-flow guidance. Deployment controls require separate evidence. |

## Boundary model

VCP context starts as untrusted input. A host may use it only after the checks
required for the relevant operation succeed. The minimum flow is:

```text
source or peer
  -> size and syntax limits
  -> versioned schema validation
  -> deterministic canonicalization
  -> integrity and provenance verification
  -> freshness, revocation, audience, scope, and region decisions
  -> capability negotiation
  -> purpose-limited projection
  -> host authorization and enforcement
  -> redacted audit record
```

Every arrow is a trust transition. Implementations fail closed when a required
security service is unavailable. Unsupported optional behavior is reported as
unsupported and never counted as a pass.

## Data classes

| Data | Typical sensitivity | Required handling |
|:---|:---|:---|
| Identity token | Linkable identifier and namespace data | Validate syntax, namespace, issuer, audience, and version |
| Signed bundle | Values, rules, and provenance | Bound size, canonicalize, hash, verify, authorize, and check revocation |
| CSM-1 expression | Compact constitutional meaning | Parse against the selected grammar and canonicalize before comparison |
| Situational context | Time, place, social setting, activity | Minimize by purpose and avoid source detail when a derived category is enough |
| Personal state | Potentially sensitive inferred or reported state | Require consent, freshness, decay, access, retention, and inference controls |
| Relational or torch state | Continuity and relationship history | Use explicit handles, scoped access, integrity protection, expiry, and revocation |

## SDK mapping

The source candidate maps the flow to the following implementation surfaces:

| Stage | Python | Rust | WebMCP |
|:---|:---|:---|:---|
| Identity and semantic parsing | Reference modules under `python/src/vcp/` | `rust/vcp-core` | Tool input validation only |
| Bundle verification | Python bundle, enforcement, revocation, and orchestrator modules | `vcp-core` transport and orchestrator | Outside the browser subset |
| Context encoding | Python adaptation context | `vcp-core` context | Demonstration tool inputs and outputs |
| Host exposure | Optional MCP server | CLI, library, and WASM calls | `document.modelContext` registration |
| Lifecycle | Process or caller-owned resources | Caller-owned values | AbortSignal-owned tool registration |

The sibling repositories are selected by the exact `source_commit` recorded
in [`status/publication-state.json`](../status/publication-state.json)
(currently `null`, meaning no commit has been pinned yet). Moving branches are
unsuitable evidence.

## MCP 2026-07-28 profile

MCP 2026-07-28 carries protocol version, client information, and capabilities
on each request. Draft VEP-0005 proposes a `space.creed.vcp/*` metadata namespace
for ambient VCP context. Explicit tool arguments remain authoritative when they
conflict with ambient metadata. Persisted application state uses explicit,
auditable handles rather than implicit transport sessions.

VEP-0005 remains draft. Implementations must negotiate the MCP revision and
must not silently apply this profile to older peers.

## Privacy and audit

Projection precedes model or tool access. The application should pass the least
specific representation that meets the declared purpose. Logs use stable event
codes and bounded metadata. They exclude API keys, raw prompts, private context,
provider response bodies, signatures, and request-state secrets.

Audit records identify the verified object, policy decision, enforcement path,
and build identity. They do not turn sensitive context into an unrestricted log
retention channel.

## Failure behavior

Required verification failures produce a stable rejection code. Transient
dependency failure remains distinguishable from confirmed invalidity while both
fail closed. User-facing text is safe and general. Detailed diagnostics stay in
redacted operational telemetry with controlled access and retention.
