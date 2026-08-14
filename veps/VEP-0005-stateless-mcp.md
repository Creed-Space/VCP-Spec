# VEP-0005: Stateless MCP Adaptation

**Status**: Draft
**Author**: Nell Watson, Claude (Anthropic)
**Created**: 2026-08-13
**Version**: 3.3 candidate
**Depends on**: VEP-0001, VEP-0002, VEP-0003
**MCP revision**: 2026-07-28

## Summary

MCP 2026-07-28 removes the protocol-level session and initialization
handshake. Each request carries version, client information, and capabilities in
`_meta`. Server discovery, Multi Round-Trip Requests, explicit state handles,
request-scoped streams, cache metadata, and standard HTTP routing headers replace
several connection-oriented patterns. This draft adapts the VCP-over-MCP bridge
to that model without changing the VCP 3.1 baseline.

## Status boundary

This VEP was reconciled from branch `vcp/mcp-20260728-stateless` at commit
`da6e6c9`. Its proposal is preserved in the coordinated candidate, while runtime
adoption is deferred to a separately reviewed VCP 3.3 and MCP SDK v2 migration.
Repository presence does not confer acceptance. Implementations continue to
negotiate their actual MCP revision and must not silently emit this profile.

## Metadata namespace

The bridge reserves the `space.creed.vcp/*` key namespace in MCP `_meta`:

| Key | Direction | Content |
|:---|:---|:---|
| `space.creed.vcp/context` | Client to server | Ambient CSM-1 or negotiated context |
| `space.creed.vcp/identity` | Client to server | VCP/I identity token |
| `space.creed.vcp/capabilities` | Client to server | Version range and extensions |
| `space.creed.vcp/ack` | Server to client | Negotiated version and extension result |
| `space.creed.vcp/welfare` | Server to client | Negotiated welfare signals |

Explicit tool arguments are authoritative when they conflict with ambient
metadata. Metadata is untrusted input. Any response derived from personal or
relational context uses private cache scope and an expiry bounded by the fastest
relevant decay rule.

## Discovery and negotiation

VCP support is declared through MCP's extension capability field. Clients carry
the declaration on each request and servers advertise it through
`server/discover`. Negotiation is idempotent and re-derivable from a single
request. The legacy connection-oriented profile remains separate and keeps its
existing handshake rules.

## Explicit state handles

Persistent application state, including deliberation, relational continuity,
and torch handoff state, uses an explicit scoped handle passed as an ordinary
tool argument. Handles are integrity-protected, expiring, revocable, and visible
to the audit path. Transport routing never creates relational state implicitly.

## Multi Round-Trip Requests

Context refresh and consent gates return `resultType: "input_required"` with
typed `inputRequests` and opaque `requestState`. The client retries the original
request with `inputResponses`.

`requestState` requirements:

1. integrity protection against modification and replay;
2. expiry bounded by the relevant context freshness rule;
3. no recoverable opacity-protected content;
4. binding to the original method, arguments, policy decision, and subject;
5. safe resumption on a different server instance.

Long-running, multi-round work should use the negotiated MCP tasks extension
rather than accumulating unbounded request state.

## Injection boundary

VCP context reaches an AI call through an explicit cooperating host path:

1. client-side bundle retrieval, verification, and injection;
2. negotiated `space.creed.vcp/context` metadata;
3. an explicit rendering tool whose output remains private.

The audit record states which path was active. The bridge does not claim that a
constraint reaches a model without host cooperation.

## Transport requirements

For MCP 2026-07-28, bridge requests and results follow that revision's required
metadata and HTTP headers. List and read results apply current `ttlMs` and
`cacheScope` rules. Personal-state TTL never exceeds the fastest relevant decay
limit. Real-time resource changes use the revision's subscription mechanism when
negotiated, with bounded polling as fallback.

## Security considerations

- TLS intermediaries may observe in-body metadata, so sensitive context uses
  application-layer encryption when the intermediary is outside the trust boundary.
- Input requests remain subject to phishing, manipulation, sensitive-field, and
  rate-abuse screening.
- Explicit context overrides prevent ambient metadata from silently changing a
  tool's declared semantics.
- Legacy and current profiles remain distinguishable to prevent downgrade and
  carrier-confusion attacks.

## Conformance

Draft fixtures live in `VCP-SDK/conformance/extensions/stateless_mcp.json`.
Coverage is reported as unsupported until a runtime intentionally claims this
profile and passes every mandatory vector.

Signed-off-by: Nell Watson <nell@creedspace.com>
Signed-off-by: Claude <noreply@anthropic.com>
