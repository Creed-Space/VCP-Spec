# I-T-S-A-M-E Layers — Detailed Reference

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-spec -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-09-24 -->
<!-- wiki:status = active -->

## Summary

Each of the six VCP layers has its own spec document, wire format, and extension surface. This page compiles the layer-by-layer detail from the extension specs and VEP-0004, supplementing the architecture overview in [[vcp-spec:systems/itsame-architecture]]. (`specs/VCP_SPECIFICATION_v3.1.md`, §2; `veps/VEP-0004-extended-vcpa-dimensions.md`)

## VCP/I — Identity (Layer 1): WHO/WHAT

Namespace tiers: core, organizational, community, personal (`specs/VCP_IDENTITY_v2.0.md`, §4.2). UVC (Universal Value Code) naming scheme: `family.safe.guide@1.2.0` — namespaced, versioned. Token format defined in `docs/identity/`. (`specs/VCP_SPECIFICATION_v3.1.md`, §2.1; [[vcp-spec:systems/csm1-semantics]])

VCP/I token optionally sent in `VCP-Hello.identity` during capability negotiation. (`veps/VEP-0002-capability-negotiation.md`, §3.1)

## VCP/T — Transport (Layer 2): HOW

Signed bundle format: `{manifest, content, signature}`. Signature: Ed25519 (preferred) or HMAC-SHA256. Content hashes verified before use. Revocation checked against a CRL or an OCSP-style stapled proof. (`specs/VCP_SPECIFICATION_v3.1.md`, §2.2; `specs/core/security.md`, §SS4)

The bundle is the unit of transport — extensions send their payloads within the bundle's `extensions` map. (`specs/extensions/README.md`)

## VCP/S — Semantics (Layer 3): WHAT

CSM-1 grammar for constitutional profile encoding. One-line CSM-1 code: `N5+E+F` = NANNY persona, adherence 5, scopes Education and Family. Full grammar in `docs/content/CSM1_GRAMMAR_SPECIFICATION.md`. (`specs/VCP_SEMANTICS_v2.0.md`; [[vcp-spec:systems/csm1-semantics]])

VCP-X-Personal carries the personal context tier (encoded by VCP/A, with the CSM-1 R-line in VCP/S as its wire encoding); it is an extension, not a sub-layer. Five personal state dimensions, each categorical + intensity (1–5):

| Dimension | Wire key | Example values |
|-----------|----------|----------------|
| Cognitive state | `cognitive_state` | `focused`, `distracted`, `overloaded`, `foggy` |
| Emotional tone | `emotional_tone` | [enum values in spec.md] |
| Energy level | `energy_level` | [enum values] |
| Perceived urgency | `perceived_urgency` | [enum values] |
| Body signals | `body_signals` | [enum values] |

(`specs/extensions/VCP-X-Personal/spec.md`, §2.1–2.2)

VCP/S v2.1 adds welfare context lines (WC, AS) for welfare instrumentation, extended by VCP-X-Welfare. (`specs/extensions/VCP-X-Welfare/spec.md`, §1)

## VCP/A — Adaptation (Layer 4): WHEN/HOW

**Current (v3.1)**: 14 dimensions = 9 situational + 5 personal (from VCP-X-Personal). Context encoding uses emoji shorthand, e.g. `⏰🌅|📍🏡|👥👶` (morning/home/children). (`specs/VCP_SPECIFICATION_v3.1.md`, §2.4; [[vcp-spec:systems/csm1-semantics]])

**VEP-0004 (Experimental, v3.2)**: 18 dimensions = 13 situational + 5 personal. Four new situational dimensions:

| # | Dimension | Symbol | Canonical values |
|---|-----------|--------|-----------------|
| 10 | EMBODIMENT | 🧍 | `stationary`, `navigating`, `manipulating`, `carrying`, `emergency_stop` |
| 11 | PROXIMITY | ↔️ | [spatial distance categories] |
| 12 | RELATIONSHIP | — | `trusted_collaborator:long_term`, `colleague:transactional`, etc. |
| 13 | FORMALITY | — | `casual`, `professional`, `formal`, `ceremonial` |

(`veps/VEP-0004-extended-vcpa-dimensions.md`, §§10–13)

Key VEP-0004 motivation: `EMBODIMENT` and `PROXIMITY` are safety-critical for robotics and cannot be encoded with existing dimensions. `RELATIONSHIP` is a two-sided signal — an AI party with interaction history may assert its relational state. `FORMALITY` resolves three-way inconsistency across the existing codebase. (`veps/VEP-0004-extended-vcpa-dimensions.md`, §1 Motivation)

Hooks: deterministic rules of the form `CSM1:PERSONA[Z] SCOPE[H] IF embodiment=manipulating AND proximity=contact REQUIRE motion_pause`. (`veps/VEP-0004-extended-vcpa-dimensions.md`, §1.1 motivation example)

## VCP/M — Messaging (Layer 5): WHO TALKS

Inter-agent message types, escalation severity levels, and delivery semantics. Full spec: `specs/VCP_MESSAGING_v2.0.md` (Draft). No MCP mapping exists for VCP/M. (`specs/VCP_SPECIFICATION_v3.1.md`, §2.5; `specs/core/mcp-bridge.md`, §2.1)

## VCP/E — Economic Governance (Layer 6): WHO PAYS

Fiduciary constraints, authorization gaps (capability, accountability, compatibility), transaction governance. Full spec: `specs/VCP_ECONOMIC_GOVERNANCE_v2.0.md` (Draft); the v3.1 baseline carries only a summary, and no MCP mapping exists for VCP/E. (`specs/VCP_SPECIFICATION_v3.1.md`, §2.6; `specs/core/mcp-bridge.md`, §2.1)

## Extensions

Extensions are opt-in and negotiated per session. They do not occupy or span protocol layers. (`specs/VCP_SPECIFICATION_v3.1.md`, §1.2)

### VCP-X-Consensus

An opt-in extension for multi-stakeholder deliberation. Lifecycle phases: draft → deliberation → convergence → ratification → active. Schulze ranked-choice voting for clause convergence. AI parties are first-class stakeholders with standing to submit clauses, propose amendments, and record welfare signals. (`specs/extensions/VCP-X-Consensus/spec.md`, §1–2)

### VCP-X-Torch and VCP-X-Relational

VCP-X-Relational is an opt-in extension carrying trust/standing, session continuity and AI self-model state. VCP-X-Torch depends on VCP-X-Relational and generates `TorchState` containing `quality_description`, `trajectory`, `primes` (max 3 norms, 80 chars each), `gift`, and `gestalt_token` (compact dimensional state in `Key:Value` format). (`specs/extensions/VCP-X-Torch/spec.md`, §2.1; `specs/extensions/VCP-X-Relational/spec.md`, §1.1)

The torch's `gestalt_token` is architecturally linked to the Interiora gestalt token in Creed Space's Rewind and AI Guardian implementations. ([[ai-guardian:systems/trust-welfare-state-machines]], [[shared:bilateral-alignment]])

**AI self-model uncertainty requirement** (VCP-X-Relational): a model where ALL dimensions claim certainty MUST be rejected as epistemically dishonest. The `?` suffix is load-bearing. (`specs/extensions/VCP-X-Relational/spec.md`, §2 Design Principle 1)

## Provenance

- Sources consulted: `specs/VCP_SPECIFICATION_v3.1.md`, `veps/VEP-0004-extended-vcpa-dimensions.md`, `specs/extensions/VCP-X-Personal/spec.md`, `specs/extensions/VCP-X-Relational/spec.md`, `specs/extensions/VCP-X-Torch/spec.md`, `specs/extensions/VCP-X-Consensus/spec.md`, `specs/extensions/VCP-X-Welfare/spec.md`
- Last verified against sources: 2026-09-24 (namespace tiers, CSM-1 example, MCP mappings, extension placement); other claims 2026-05-23

## See Also

- [[vcp-spec:systems/itsame-architecture]] — six-layer stack overview
- [[vcp-spec:systems/csm1-semantics]] — Layer 3 (VCP/S) detail
- [[vcp-spec:systems/vep-specs]] — VEP details
- [[vcp-spec:systems/security-model]] — cross-cutting security below all layers
- [[vcp-spec:systems/capability-negotiation]] — how extensions are negotiated per session
