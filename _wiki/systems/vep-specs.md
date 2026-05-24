# VEP Specifications — All Filed VEPs

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-spec -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-05-23 -->
<!-- wiki:status = active -->

## Summary

Four VEPs (VCP Enhancement Proposals) have been filed as of v3.1+. VEP-0001 through VEP-0003 are Accepted and part of the stable v3.1 spec. VEP-0004 is Experimental, targeting a v3.2 pre-release. (`veps/VEP-000*`, `specs/VCP_SPECIFICATION_v3.1.md`)

## VEP-0001: Extension Model Architecture (Accepted)

**Status**: Accepted | **Authors**: Nell Watson, Claude (Anthropic) | **Version**: 3.1

Establishes the `VCP-X-{Name}` naming convention for opt-in extensions. Each extension must provide: spec.md, schema.json, wire format examples, reference implementation, and conformance tests. Extension lifecycle: `EXPERIMENTAL → STABLE → DEPRECATED → REMOVED` with minimum durations (6 months for Stable, 12 months for Deprecated). (`veps/VEP-0001-extension-model.md`)

Extension dependency declarations: VCP-X-Torch depends on VCP-X-Relational. VCP-X-Intent depends on VCP-X-Personal and VCP-X-Relational. Others have no declared dependencies. (`veps/VEP-0001-extension-model.md`, dependency table)

## VEP-0002: Capability Negotiation Protocol (Accepted)

**Status**: Accepted | **Depends on**: VEP-0001 | **Version**: 3.1

Defines the `VCP-Hello` / `VCP-Ack` / `VCP-Error` message types for per-session version and extension negotiation. Key design goals:
- Zero-cost for legacy clients (5-second timeout fallback assumes VCP 1.0)
- Fail-closed on version mismatch
- Extension isolation (unsupported extensions reported, do not cause connection failure)
- MCP compatibility (piggybacks on MCP `initialize` flow)

(`veps/VEP-0002-capability-negotiation.md`, "Design Goals")

VCP-Hello fields: `type`, `version`, `min_version`, `extensions`, `identity`, `client_id`. VCP-Ack fields: `type`, `version`, `supported`, `unsupported`, `capabilities`, `core_features`. (`veps/VEP-0002-capability-negotiation.md`, message definitions)

## VEP-0003: VCP-over-MCP Bridge (Accepted)

**Status**: Accepted | **Depends on**: VEP-0001, VEP-0002 | **Version**: 3.1

Maps VCP to MCP primitives. VCP state exposed as `vcp://` URI resources; VCP operations exposed as `vcp_*` MCP tools. Capability negotiation maps to MCP `initialize` handshake.

Key resources:

| URI | Content |
|-----|---------|
| `vcp://bundle/{session_id}` | Full VCP bundle |
| `vcp://identity/{token}` | Parsed identity token |
| `vcp://constitution/{csm1_code}` | Decoded constitutional profile |
| `vcp://capabilities` | Supported extensions |
| `vcp://personal-state/{session_id}` | VCP-X-Personal state (if negotiated) |

Key tools: `vcp_validate_token`, `vcp_parse_csm1`, `vcp_encode_context`, `vcp_status` (core); `vcp_set/get_personal_state`, `vcp_submit_ballot`, `vcp_generate_torch` (extensions). (`veps/VEP-0003-mcp-bridge.md`)

MCP sampling integration: active VCP bundle is injected as system prompt prefix into every sampling request — constitutional constraints travel WITH the LLM call. (`veps/VEP-0003-mcp-bridge.md`, "Sampling Integration")

## VEP-0004: Extended VCP/A Dimensions (Experimental)

**Status**: Experimental | **Author**: Nell Watson | **Targets**: VCP 3.2 pre-release

Extends the VCP/A situational dimension set from 9 to 13 by adding four new dimensions. Total VCP/A count moves from 14 (9 situational + 5 personal) to 18 (13 situational + 5 personal). Existing dimensions 1–9 retain their identity unchanged. (`veps/VEP-0004-extended-vcpa-dimensions.md`)

New dimensions:

| # | Name | Symbol | Motivation | Values |
|---|------|--------|-----------|--------|
| 10 | EMBODIMENT 🧍 | Motor state | Robotics safety-critical | `stationary`, `navigating`, `manipulating`, `carrying`, `emergency_stop` |
| 11 | PROXIMITY ↔️ | Spatial distance | Physical space interaction protocols | [spec in VEP-0004] |
| 12 | RELATIONSHIP | Relational tie | Bilateral relational modelling, two-sided signal | [spec in VEP-0004] |
| 13 | FORMALITY | Register | Resolves inconsistency across core/vcp-lite/SDK | `casual`, `professional`, `formal`, `ceremonial` |

EMBODIMENT defaults to `stationary` for text-only agents (may be omitted from wire encoding). FORMALITY resolves three-way inconsistency: previously defined in core/security.md, vcp-lite schema, and vcp-sdk-python v0.2.0 as different fields. (`veps/VEP-0004-extended-vcpa-dimensions.md`, §1–3)

## Provenance

- Sources consulted: `veps/VEP-0001-extension-model.md`, `veps/VEP-0002-capability-negotiation.md`, `veps/VEP-0003-mcp-bridge.md`, `veps/VEP-0004-extended-vcpa-dimensions.md`, `specs/VCP_SPECIFICATION_v3.1.md`
- Last verified against sources: 2026-05-23

## See Also

- [[vcp-spec:systems/itsame-architecture]] — the layers VEPs extend
- [[vcp-spec:domain/extension-model]] — extension registry and lifecycle
- [[vcp-spec:systems/capability-negotiation]] — capability negotiation detail
- [[vcp-spec:systems/security-model]] — security specification for v3.1
