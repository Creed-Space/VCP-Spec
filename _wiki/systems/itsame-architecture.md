# VCP I-T-S-A-M-E Architecture

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-spec -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-05-23 -->
<!-- wiki:status = active -->

## Summary

VCP is a six-layer protocol stack for transporting constitutional values, behavioral rules, and personal context to AI systems. Layers are named I-T-S-A-M-E ("It's-a me!"), bottom to top: Identity, Transport, Semantics, Adaptation, Messaging, Economic Governance. (VCP-Spec/README.md, "Architecture")

## Core Problem VCP Solves

LLMs are "dumb receivers" — they cannot verify signatures, resolve references, or check hashes. VCP's solution: verify at the orchestration layer, inject complete validated text into the model context. (VCP-SDK/CLAUDE.md, "Core insight")

VCP and MCP are complementary: MCP moves tool data; VCP encodes what matters about that data. The VCP-over-MCP bridge makes VCP tokens travel as MCP resources. (VCP-Spec/README.md, "How VCP Relates to MCP")

## The Six Layers

| # | Layer | Mnemonic | Concern |
|---|-------|----------|---------|
| 1 | VCP/I — Identity | WHO/WHAT | Token format, namespace tiers, UVC naming |
| 2 | VCP/T — Transport | HOW | Signed bundle format, manifests, trust anchors |
| 3 | VCP/S — Semantics | WHAT | CSM-1 constitutional encoding, personas, composition |
| 4 | VCP/A — Adaptation | WHEN/HOW | Context dimensions, state machine, hooks |
| 5 | VCP/M — Messaging | WHO TALKS | Inter-agent message types, escalation severity |
| 6 | VCP/E — Economic Gov | WHO PAYS | Fiduciary constraints, authorization gaps, transactions |

(VCP-Spec/README.md, "The six layers")

## Core Security (v3.1)

Cross-cutting security below the layer stack: context encryption, injection scanning, context opacity, revocation infrastructure, tamper-evident audit chain. (VCP-Spec/README.md, "Core security")

## Extensions Model (VCP-X-*)

Six opt-in protocol extensions negotiated per session via capability handshake (VCP-Spec/README.md, "Extensions"; VCP-Spec/specs/extensions/VCP-X-Welfare/spec.md):

| Extension | Status |
|-----------|--------|
| VCP-X-Personal | Stable — 5 personal state dimensions with decay |
| VCP-X-Relational | Stable — trust, standing, AI self-model |
| VCP-X-Consensus | Stable — Schulze voting for multi-stakeholder deliberation |
| VCP-X-Torch | Stable — session handoff for relational continuity |
| VCP-X-Intent | Experimental — transparent intent inference from personal state |
| VCP-X-Welfare | Experimental — embodied welfare instrumentation (extended AS-line for robotics, temporal patterns, multi-agent aggregation, attestation chain) (`specs/extensions/VCP-X-Welfare/spec.md` v1.0.0) |

## MCP Bridge Mapping

VCP layers map to MCP primitives (VCP-Spec/README.md, "MCP Bridge"):

| VCP Layer | MCP Primitive |
|-----------|--------------|
| Identity | Tools (`vcp_validate_token`) |
| Transport | Resources (`vcp://bundle/*`) |
| Semantics | Tools + Resources |
| Adaptation | Resources + Sampling integration |
| Messaging | Tools (`vcp_send_message`, `vcp_escalate`) |
| Economic Gov | Tools (`vcp_authorize_transaction`) + Resources |

## Specification Status

All six layers: Stable as of v3.1. (VCP-Spec/README.md, "Specification Status")

Filed VEPs: VEP-0001 (Extension Model, Accepted), VEP-0002 (Capability Negotiation, Accepted), VEP-0003 (VCP-over-MCP Bridge, Accepted). (VCP-Spec/README.md, "Filed VEPs")

## Provenance

- Sources consulted: VCP-Spec/README.md, VCP-SDK/CLAUDE.md, VCP-Spec/specs/extensions/VCP-X-Welfare/spec.md
- Last verified against sources: 2026-05-23

## See Also

- [[shared:vcp]] — shared concept page: what VCP is across all projects
- [[vcp-spec:domain/extension-model]] — extension model detail
- [[vcp-spec:systems/csm1-semantics]] — CSM-1 token format (Layer 3)
- [[vcp-sdk:systems/sdk-architecture]] — reference implementation of this stack
