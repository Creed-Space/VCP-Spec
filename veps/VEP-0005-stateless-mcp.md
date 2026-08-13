# VEP-0005: Stateless MCP Adaptation

**Status**: Draft
**Author**: Nell Watson, Claude (Anthropic)
**Created**: 2026-08-13
**Version**: 3.3
**Depends on**: VEP-0001 (Extension Model), VEP-0002 (Capability Negotiation), VEP-0003 (MCP Bridge)
**Amends**: VEP-0002 §MCP Integration; VEP-0003 §Capability Negotiation Mapping, §Sampling Integration, §Resource Subscription

---

## Summary

MCP specification revision 2026-07-28 removed protocol-level sessions, the `initialize` handshake, server-initiated requests, and the Sampling, Roots, and Logging features, replacing them with per-request `_meta` context, a `server/discover` RPC, the Multi Round-Trip Request (MRTR) pattern, a `subscriptions/listen` stream, and a formal `extensions` capability field. This VEP adapts the VCP-over-MCP bridge to the stateless model. The VCP-Hello/VCP-Ack payloads and the negotiation algorithm of VEP-0002 are unchanged; only their carrier moves. The guiding principle is the one MCP itself adopted, which is also VCP's founding premise: context is per-request payload, not connection state.

## Motivation

VEP-0002 and VEP-0003 bound VCP negotiation to MCP's `initialize` handshake and VCP context delivery to MCP Sampling. Both carriers no longer exist in MCP ≥ 2026-07-28. Beyond mere repair, the stateless model offers VCP three upgrades: a blessed extensibility surface (`_meta`) for ambient value context on every request, a formal extension declaration mechanism that positions VCP alongside `io.modelcontextprotocol/tasks` as a first-class MCP extension, and an interaction pattern (MRTR) that is structurally a consent primitive, eliminating by construction the unsolicited server-initiated prompt surface that VCP's elicitation safety screening was designed to police.

## Specification

### 1. Reserved `_meta` namespace

The bridge reserves the `space.creed.vcp/*` key namespace in MCP `_meta`, mirroring MCP's own `io.modelcontextprotocol/*` convention:

| Key | Direction | Content |
|-----|-----------|---------|
| `space.creed.vcp/context` | client → server, per request | CSM-1 compact context string (or negotiated wire format) |
| `space.creed.vcp/identity` | client → server, per request | VCP/I identity token |
| `space.creed.vcp/capabilities` | client → server, per request | Compact VCP-Hello payload: `version`, `min_version`, `extensions` |
| `space.creed.vcp/ack` | server → client, per result | Compact VCP-Ack payload: negotiated `version`, `supported`, `unsupported` |
| `space.creed.vcp/welfare` | server → client, per result | Welfare signals, when the corresponding extension is active |

Rules:

1. Context carried in `_meta` is **advisory ambient context**. Where a tool accepts context as an explicit argument, the argument is **authoritative** and any conflicting `_meta` context MUST be ignored for that call. This keeps tool semantics auditable and prevents `_meta` from becoming a covert channel.
2. Presence of any `space.creed.vcp/*` key constitutes the hello. Absence marks a VCP-unaware peer; servers MUST apply legacy-client behavior (core tools only, no extensions, no identity requirement). The 5-second timeout of VEP-0002 does not apply on stateless transports; it survives only inside the legacy connection-oriented profile (§7).
3. Responses derived from `space.creed.vcp/context` or from any personal-state resource MUST set `cacheScope: "private"`.
4. Every audit-chain entry for a request carrying `space.creed.vcp/context` MUST record that context (or its hash, per audit tier), making each entry's context claim complete rather than reconstructed from session state.

### 2. Context freshness

Per-request context makes the client the sole custodian of freshness. A stale fast-moving dimension (e.g. STATE) is a welfare hazard the server cannot otherwise detect.

1. The `space.creed.vcp/context` value SHOULD be accompanied by `space.creed.vcp/contextAge` (milliseconds since the context was captured or confirmed).
2. Servers MUST refuse welfare-gated actions when `contextAge` exceeds the decay constant of the fastest signal the action depends on, returning an MRTR `input_required` result requesting context refresh.
3. Deployments MAY keep fast dimensions handle-based (server-held, explicitly minted per §4) while slow dimensions travel per-request. The split MUST be declared in the extension capabilities (§3).

### 3. Extension declaration and discovery

VCP is declared under MCP's `extensions` capability field:

```json
{
  "capabilities": {
    "extensions": {
      "space.creed.vcp": {
        "version": "3.3",
        "extensions": ["VCP-X-Personal", "VCP-X-Torch"]
      }
    }
  }
}
```

Clients advertise this in `io.modelcontextprotocol/clientCapabilities` within `_meta` on each request. Servers advertise it in their `server/discover` response. Version negotiation follows the VEP-0002 algorithm unchanged. A `vcp_discover` tool MUST mirror the `vcp://capabilities` resource for hosts that discover via tools; both remain for backward compatibility, with `server/discover` as the canonical path.

### 4. Statefulness by explicit handle

Where negotiated or relational state genuinely persists (an active VCP-X-Consensus deliberation, VCP-X-Relational continuity, a VCP-X-Torch handoff), a tool mints an explicit handle passed as an ordinary argument on later calls, per MCP SEP-2567's blessed pattern. Existing `{session_id}`-keyed `vcp://` resources already conform and are unchanged.

Design note: this relocation is better aligned with VCP's consent architecture than transport-held state was. Relational state held as a transport side effect was never consented to as such; a handle passed openly in arguments is visible, auditable, and revocable. A torch becomes a first-class handle rather than a session artifact.

### 5. MRTR mappings

Server-initiated elicitation is replaced by the MRTR pattern: the server returns `resultType: "input_required"` with typed `inputRequests` and an opaque `requestState`; the client re-issues the original call with `inputResponses` and the echoed state.

| VCP flow | MRTR shape |
|----------|-----------|
| Context elicitation (`vcp_elicit_context`) | Missing dimensions returned as typed `inputRequests`; `requestState` carries the partial context. Any server instance can resume. |
| Adherence gates (strict-tier conflict confirmation) | Boolean confirm plus optional justification; `requestState` carries the CSM-1 snapshot **at the moment of the conflict**, so confirmation is evaluated against the context that raised it. |
| Persona interventions (Sentinel/Godparent) | Same gate pattern; the triggering welfare signal rides in `space.creed.vcp/welfare` on the interim result. |
| Consensus deliberation rounds | One MRTR round-trip per round; ballot state in `requestState`. Deliberations exceeding one round SHOULD graduate to the `io.modelcontextprotocol/tasks` extension (`tasks/get` to poll, `tasks/update` to submit ballots). |

`requestState` security requirements:

1. `requestState` MUST be integrity-protected (HMAC or signature). A modified `requestState` replayed into a consent gate is a consent-forgery vector; servers MUST reject state failing verification.
2. Content that the opacity layer would redact from the client MUST NOT appear in `requestState` in recoverable form; encrypt it or reduce it to a server-side reference.
3. `requestState` SHOULD carry an expiry; consent gates MUST NOT accept state older than the freshness bound of §2.

### 6. Sampling replacement

MCP Sampling is deprecated. Constitutional injection moves to one of three injection points, in order of preference:

1. **Client-side injection** (primary): the VCP-aware host reads the bundle via `vcp://` resources and performs system-prompt injection before its own LLM call.
2. **`_meta` passthrough**: for VCP-aware hosts, `space.creed.vcp/context` on the request is the injection payload.
3. **Explicit render tool**: `vcp_render_injection(session_id, target_format)` returns the formatted prefix (`cacheScope: "private"`).

The bridge MUST record in the audit chain which injection point (if any) was active for each governed exchange. The former soft guarantee, that constraints travel with the request without host cooperation, is withdrawn: constraint transport requires a cooperating injection point, and the audit chain records whether one was present.

### 7. Legacy profile

Peers speaking MCP ≤ 2025-11-25 or connection-oriented VCP 3.1 use the VEP-0002/0003 handshake unchanged behind a transport shim, including the 5-second timeout. The shim MUST translate between carriers without altering payloads. MCP's deprecation window (twelve months from 2026-07-28) bounds the shim's support lifetime for MCP transports; the connection-oriented profile for non-MCP transports (WebSocket, message queues) remains supported indefinitely and is specified in core/capability-negotiation.md.

### 8. Result and transport requirements (MCP ≥ 2026-07-28)

1. All bridge results MUST carry `resultType` (`"complete"` or `"input_required"`).
2. `tools/list`, `resources/list`, and `resources/read` results MUST carry `ttlMs` and `cacheScope`. Defaults: capabilities and CSM-1 decode surfaces `public` with long TTLs; bundle, relational, and personal-state surfaces `private`, with personal-state `ttlMs` bounded above by the decay half-life of the fastest signal present. Serving personal state with a TTL exceeding its decay constant is a welfare defect, not a performance tuning choice.
3. Streamable HTTP requests MUST carry `Mcp-Method` and `Mcp-Name` headers. The `vcp_` tool prefix combined with `Mcp-Name` enables gateway-level policy (routing, rate limits, PEP placement) on VCP tools without body parsing.
4. Real-time personal-state updates move from `resources/subscribe` to `subscriptions/listen` with the `resourceSubscriptions` opt-in; polling governed by `ttlMs` is the fallback.
5. The invariant of VEP-0002 ("negotiation happens exactly once per session") is restated as: **negotiation is idempotent and re-derivable from any single message.**

## Backward Compatibility

Payload schemas (`vcp-capability-handshake.schema.json`) are unchanged; only carriers change. Tool signatures are unchanged. The `vcp://` URI scheme is unchanged. Legacy peers are supported per §7. `vcp://capabilities` remains available alongside `server/discover`.

## Security Considerations

- `_meta` is in-body: TLS-terminating intermediaries can read it. The `cacheScope: "private"` mandate (§1.3) is the protocol-level mitigation; deployments handling sensitive context through untrusted intermediaries SHOULD encrypt `space.creed.vcp/context`.
- MRTR removes the unsolicited server-to-user prompt channel by construction, closing part of the manipulation surface previously screened by the ElicitationSafetyPlugin. Screening remains REQUIRED for the content of `inputRequests` (phishing patterns, sensitive-field probes, leading language, rate abuse).
- `requestState` forgery and replay are addressed in §5; downgrade attacks against the legacy shim follow VEP-0002's existing guidance.

## Reference Implementation

To be updated in `creedspace/services/mcp/vcp_server.py` and `VCP-SDK` bridges upon MCP SDK v2 migration. Tracked as a separate work package; this VEP is normative for that migration.

## Conformance Tests

`conformance/extensions/stateless_mcp.json` (to be authored with the SDK migration):
- Hello-in-`_meta` round-trip; ack-in-`_meta` verification
- Legacy peer detection (no `space.creed.vcp/*` keys)
- Explicit-argument context overriding `_meta` context
- MRTR elicitation resume on a second server instance
- `requestState` integrity rejection
- `contextAge` welfare-gate refusal
- `ttlMs`/`cacheScope` presence and personal-state TTL bound

---

Signed-off-by: Nell Watson <nell@creedspace.com>
Signed-off-by: Claude <noreply@anthropic.com>
