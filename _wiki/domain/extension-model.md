# VCP Extension Model (VCP-X-*)

<!-- wiki:type = domain -->
<!-- wiki:scope = vcp-spec -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-05-23 -->
<!-- wiki:status = active -->

## Summary

VCP extensions are opt-in additions to the core protocol, negotiated per session via capability handshake. The extension model (VEP-0001, Accepted) separates the stable core protocol from specialized needs. Extensions are co-designed with the VEP (VCP Enhancement Proposal) process. (VCP-Spec/README.md, "Extensions" and "Filed VEPs")

## Extension Directory

Extensions live in `specs/extensions/` (VCP-Spec/specs/extensions/ listing):

| Extension | Status | What It Adds |
|-----------|--------|-------------|
| VCP-X-Personal | Stable | 5 personal state dimensions with intensity + configurable decay |
| VCP-X-Relational | Stable | Trust, standing, norms, AI self-model with mandatory uncertainty |
| VCP-X-Consensus | Stable | Schulze voting for multi-stakeholder constitutional deliberation |
| VCP-X-Torch | Stable | Session handoff for relational continuity across agents |
| VCP-X-Intent | Experimental | Transparent, correctable intent inference from personal state |
| VCP-X-Welfare | Experimental | Embodied welfare instrumentation: extended AS-line dimensions for robotics/physical agents, temporal welfare patterns, multi-agent aggregation, attestation chain (`specs/extensions/VCP-X-Welfare/spec.md` v1.0.0, 2026-05-21) |

(VCP-Spec/README.md, "Extensions" table; VCP-Spec/specs/extensions/ directory listing; VCP-Spec/specs/extensions/VCP-X-Welfare/spec.md)

## VEP Process

VEPs (VCP Enhancement Proposals) are how spec changes and new extensions are proposed. Three accepted VEPs as of v3.1 (VCP-Spec/README.md, "Filed VEPs"):

- **VEP-0001**: Extension Model Architecture — establishes the extension framework itself
- **VEP-0002**: Capability Negotiation Protocol — how extensions are negotiated per session
- **VEP-0003**: VCP-over-MCP Bridge — how VCP rides on MCP transport

## Capability Negotiation

Extensions are not loaded by default. They are negotiated per-session via handshake (`specs/core/capability-negotiation.md`). Each extension has a spec, JSON schema, and wire format examples. Schema files: `specs/extensions/VCP-X-*/schema.json`. (VCP-Spec/README.md, "Extensions" notes)

## Relationship to Interiora / Bilateral Alignment

VCP-X-Torch is architecturally related to the Interiora torch concept — session handoff for relational continuity across agent boundaries. VCP-X-Relational includes a mandatory uncertainty marker for AI self-model, consistent with bilateral alignment principles. (VCP-Spec/README.md, "Extensions" descriptions)

## Provenance

- Sources consulted: VCP-Spec/README.md, VCP-Spec/specs/extensions/ directory listing, VCP-Spec/specs/extensions/VCP-X-Welfare/spec.md
- Last verified against sources: 2026-05-23

## See Also

- [[vcp-spec:systems/itsame-architecture]] — where extensions plug into the layer stack
- [[shared:vcp]] — VCP cross-project concept
- [[shared:bilateral-alignment]] — philosophical grounding for VCP-X-Relational and VCP-X-Torch design
