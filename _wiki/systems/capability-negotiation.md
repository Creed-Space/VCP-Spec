# Capability Negotiation Protocol

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-spec -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-05-23 -->
<!-- wiki:status = active -->

## Summary

Capability negotiation is a single-round-trip handshake (VCP-Hello → VCP-Ack) that establishes the protocol version and active extension set for a VCP session before any context data is exchanged. Defined in `specs/core/capability-negotiation.md` and formalized by VEP-0002. Legacy VCP 1.0 clients without handshake support are handled via 5-second timeout fallback. (`specs/core/capability-negotiation.md`, `veps/VEP-0002-capability-negotiation.md`)

## Message Flow

```
Client                          Server
  |  ------ VCP-Hello ------->  |
  |  <------ VCP-Ack ---------  |   (success)
  |       OR                    |
  |  <------ VCP-Error --------  |   (version mismatch)
  |                              |
  |  === VCP session active ===  |
```

For legacy clients (no VCP-Hello within 5 seconds): server assumes VCP 1.0, no extensions, core-only. (`specs/core/capability-negotiation.md`, §2.1)

## VCP-Hello Fields

Sent client → server:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | REQUIRED | Always `"vcp-hello"` |
| `version` | string | REQUIRED | Preferred VCP version (semver minor, e.g. `"3.1"`) |
| `min_version` | string | OPTIONAL | Minimum acceptable version. Default `"1.0"` |
| `extensions` | string[] | OPTIONAL | Desired extensions. Default `[]` |
| `identity` | string\|null | OPTIONAL | VCP/I identity token |
| `client_id` | string | OPTIONAL | Client identifier (e.g. `"creedspace-web/2.4.0"`) |

(`specs/core/capability-negotiation.md`, §3.1; `veps/VEP-0002-capability-negotiation.md`)

## VCP-Ack Fields

Sent server → client:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | REQUIRED | Always `"vcp-ack"` |
| `version` | string | REQUIRED | Negotiated version (≤ preferred, ≥ min) |
| `supported` | string[] | REQUIRED | Extensions server will activate |
| `unsupported` | string[] | REQUIRED | Extensions server cannot provide |
| `capabilities` | object | OPTIONAL | Per-extension capability details |
| `core_features` | object | OPTIONAL | Active core security features |

(`specs/core/capability-negotiation.md`, §3.2; `veps/VEP-0002-capability-negotiation.md`)

## VCP-Error

Server → client on version mismatch:

```json
{
  "type": "vcp-error",
  "code": "VERSION_UNSUPPORTED",
  "message": "human-readable description",
  "supported_versions": ["1.0", "1.1"]
}
```

Server MUST reject (send VCP-Error) if it cannot satisfy `min_version`. Server MUST NOT reject due to unsupported extensions — those are reported in `unsupported` within a normal VCP-Ack. (`specs/core/capability-negotiation.md`, §3.3; `veps/VEP-0002-capability-negotiation.md`, "Design Goals")

## Extension Isolation Guarantee

Unsupported extensions in the `extensions` request list are acknowledged in `vcp-ack.unsupported` but do not cause connection failure. Only the intersection of client-requested and server-supported extensions is active. Clients MUST NOT send extension-specific payload for non-negotiated extensions. (`veps/VEP-0001-extension-model.md`, "Extension Negotiation"; `specs/extensions/README.md`)

## MCP Mapping

VCP-Hello maps to `MCP initialize.params.initializationOptions.vcp`. VCP-Ack maps to `MCP initialize.result.serverInfo.metadata.vcp`. If no `vcp` key in MCP init options, server assumes VCP 1.0 (core only). (`veps/VEP-0003-mcp-bridge.md`, "Capability Negotiation Mapping")

## Extension Lifecycle States

Managed by the extension model (VEP-0001):

| State | Min Duration | Breaking changes |
|-------|-------------|-----------------|
| EXPERIMENTAL | 6 months before → STABLE | Wire format may change; implementations SHOULD support but MAY drop without deprecation |
| STABLE | 12 months before → DEPRECATED | Wire format frozen; changes require new extension (e.g. VCP-X-Personal-v2) |
| DEPRECATED | 12 months before → REMOVED | Implementations MUST support for 12 months |
| REMOVED | — | No longer part of specification |

(`veps/VEP-0001-extension-model.md`, "Extension Lifecycle")

## Current Extension Status (v3.1)

| Extension | Status |
|-----------|--------|
| VCP-X-Personal | Stable |
| VCP-X-Relational | Stable (Draft in spec.md) |
| VCP-X-Consensus | Stable (Draft in spec.md) |
| VCP-X-Torch | Stable |
| VCP-X-Intent | Experimental |
| VCP-X-Welfare | Experimental |

(`specs/VCP_SPECIFICATION_v3.1.md`, extension table; individual spec.md files)

## Provenance

- Sources consulted: `specs/core/capability-negotiation.md`, `veps/VEP-0001-extension-model.md`, `veps/VEP-0002-capability-negotiation.md`, `veps/VEP-0003-mcp-bridge.md`, `specs/extensions/README.md`
- Last verified against sources: 2026-05-23

## See Also

- [[vcp-spec:systems/itsame-architecture]] — full layer stack
- [[vcp-spec:domain/extension-model]] — extension model and VEP process
- [[vcp-spec:systems/vep-specs]] — individual VEP content
- [[vcp-spec:systems/security-model]] — core_features negotiated in VCP-Ack
