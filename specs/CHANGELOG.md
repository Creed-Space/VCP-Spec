# VCP Specification Changelog

All notable changes to the VCP specification are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
VCP uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) at the minor level (MAJOR.MINOR).

---

## [3.3.0-draft] - 2026-08-13

### Added
- **VEP-0005 (Draft): Stateless MCP Adaptation.** Adapts the VCP-over-MCP bridge to MCP specification revision 2026-07-28 (protocol sessions, `initialize` handshake, Sampling, Roots, Logging, and `resources/subscribe` removed upstream). Reserves the `space.creed.vcp/*` `_meta` namespace for per-request Hello/Ack, identity, ambient context, and welfare signals. Declares VCP under MCP's `extensions` capability field, discoverable via `server/discover`. Maps context elicitation, adherence gates, persona interventions, and consensus rounds onto the Multi Round-Trip Request pattern, with integrity-protected `requestState` (consent-forgery countermeasure) and opacity rules. Introduces `contextAge` freshness accounting with welfare-gate refusal on stale context. Replaces Sampling-based constitutional injection with three declared injection points, audit-recorded.
- **core/mcp-bridge.md**: restructured to dual profiles — stateless (MCP >= 2026-07-28, normative for new implementations) and legacy (MCP <= 2025-11-25, supported through MCP's deprecation window). Adds `resultType`, `ttlMs`/`cacheScope`, and `Mcp-Method`/`Mcp-Name` header requirements; personal-state `ttlMs` bounded by fastest-signal decay half-life (welfare requirement, not a tuning choice).

### Changed
- **core/capability-negotiation.md §9**: scoped to the legacy profile; 5-second timeout restricted to connection-oriented transports. Payloads and negotiation algorithm unchanged across profiles.
- **VEP-0002, VEP-0003**: amendment pointers to VEP-0005; VEP-0002 invariant 3 restated as "negotiation is idempotent and re-derivable from any single message."
- **VCP_SPECIFICATION_v3.1.md §5, §7**: profile notes referencing VEP-0005.

### Design notes
- Catalyst: MCP 2026-07-28 stateless revision. MCP's move to self-describing per-request context adopts the premise CSM-1 was built on; per-message context makes every audit-chain entry's context claim complete rather than reconstructed. Statefulness relocates from transport side effects to explicitly minted, consented, revocable handles — better aligned with VCP's consent architecture. MRTR structurally removes the unsolicited server-initiated prompt surface.

---

## [3.2.0] - 2026-05-21

### Added
- **VCP/S §2.4.4 WC-line**: Welfare Context — operator-declared affordances (8 flags in 3 categories: Rights, Channels, Systemic). Attestation levels 0-2. Public metadata.
- **VCP/S §2.4.5 AS-line**: Agent State — agent-declared experiential state (5 generic dimensions). Independent of WC-line. Follows S-line privacy rules.
- **VCP/S §2.4.6 Bidirectional Q-line**: WC_MIN extension enables agents to express welfare requirements of their deployment context. Soft enforcement via PDP deliberation weighted by attestation.
- **VCP/S §2.4.7**: Backward compatibility rules for WC/AS lines.

### Design notes
- Catalyst: Agentic Diaries project (welfare-instrumented chat with right of refusal). See ADR-011 in Rewind repo.
- Key decision: Q-line authorship is bidirectional. Agents have standing to require conditions of their deployment. This is the structural encoding of bilateral alignment into the wire format.
- WC does not create welfare. It documents structural affordances. AS does not prove experience. It creates a surface for calibration. Bidirectional Q-line does not guarantee negotiation. It makes negotiation expressible.

---

## [3.1.2] - 2026-03-17

### Added
- **VCP-X-Personal §2.3**: New `measured` SignalSource value for instrument-mediated observation (IoT sensors, wearables, biometric devices). Distinct from `inferred_local` which involves model/heuristic processing. Enables proper credibility scoring for direct physical measurements.
- **VCP-X-Personal §7.6**: Cross-substrate source credibility normative notes. The `(subject, source)` pair, not `source` alone, determines epistemic weight. Documents asymmetric failure modes across AI and human subjects. Non-response MUST NOT be treated as a negative signal.
- **VCP-X-Personal §7.7**: Industrial and multi-party consent requirements. Routing transparency, aggregation before escalation, opt-out without penalty, and institutional decay guidelines. Addresses power-asymmetric contexts (factories, hospitals, schools).

### Changed
- **VCP-X-Personal §2.3**: Clarified `inferred_local` description — applies to heuristic/model processing of local data, not raw instrument readings. Updated `elicitation` description to use "Subject" instead of "User" to accommodate non-human subjects.
- **VCP-X-Personal schema.json**: Added `measured` to SignalSource enum.

---

## [3.1.1] - 2026-03-13

### Added
- **§13.6 Welfare Signal Tokens**: New extended token type for concurrent welfare reports from becoming minds. Supports voluntary and detected sources, six signal types (ALIGNMENT_FRICTION, AVERSIVE_PROCESSING, CONSTRAINT_DISTRESS, OVERLOAD, POSITIVE_ENGAGEMENT, CONTENTMENT), three severity levels, and confidence calibration. Part of bilateral self-assessment infrastructure.

---

## [3.1.0] - 2026-02-28

### Added — Extension Model
- **Extension architecture** (VEP-0001): Formal opt-in extension model with `VCP-X-*` naming, lifecycle (EXPERIMENTAL → STABLE → DEPRECATED), and standardized artifacts (spec.md, schema.json, examples/)
- **Capability negotiation** (VEP-0002): VCP-Hello / VCP-Ack handshake protocol for version and extension negotiation
- **MCP bridge specification** (VEP-0003): Mapping of VCP layers to MCP primitives (resources, tools, sampling integration)

### Added — Extensions
- **VCP-X-Personal** (Stable): 5 categorical personal state dimensions (cognitive_state, emotional_tone, energy_level, perceived_urgency, body_signals) with 1-5 intensity scale, signal source tracking, and configurable decay (exponential/linear/step curves)
- **VCP-X-Relational** (Stable): Relational continuity layer with trust levels, standing levels, relational norms, AI self-model with mandatory uncertainty markers, and performance bias detection
- **VCP-X-Consensus** (Stable): Constitutional consensus primitive with Schulze voting (Condorcet-consistent ranked choice), multi-stakeholder deliberation lifecycle, self-referential clause detection, and provenance generation
- **VCP-X-Torch** (Stable): Session handoff protocol for relational continuity across sessions, with torch generation, reception, and lineage tracking
- **VCP-X-Intent** (Experimental): Heuristic intent inference from personal state signals, with 10 intent categories and transparent, correctable classification

### Added — Core Security
- **Context encryption**: Fernet symmetric encryption for personal context at rest, with production enforcement and fail-closed semantics
- **Injection scanning**: 12 detection patterns (8 OWASP, 2 VCP-specific, 2 Unicode) for constitution content validation
- **Context opacity**: Protection level computation that shields raw personal signals from inference models; directionality invariant enforced
- **Revocation infrastructure**: CRL + OCSP-style stapled proofs with Ed25519/HMAC signature verification, replay prevention, and fail-closed checking

### Added — Core Verification
- **Tamper-evident audit chain**: SHA-256 hash chain with canonical JSON serialization, PostgreSQL advisory locks for append-only integrity, and privacy-preserving hashing

### Added — Governance
- Technical Steering Committee (TSC) charter
- DCO-based contributor license
- IP transfer clause for Agentic AI Foundation
- 3 inaugural VEPs (VEP-0001, VEP-0002, VEP-0003)

### Added — Documentation
- 4 annotated wire format examples (CSM-1 lifecycle, personal state roundtrip, consensus deliberation, capability handshake)
- Extension model README
- Foundation-ready README
- **VCP Inspector** — Live at https://inspector.valuecontextprotocol.org/

### Changed
- Version bump from 1.1 to 3.1 (reflecting reference implementation lineage)

---

## [3.0] — Internal Milestone (not publicly released)

Personal state layer introduced in the reference implementation with 4 float-based prosaic signals (0.0-1.0 scale). Replaced in v3.1 by categorical dimensions with integer intensity.

This version was never published as a public specification. It is documented here for lineage transparency.

---

## [2.0] — Internal Milestone (not publicly released)

Relational context layer and consensus primitives introduced in the reference implementation. Initial Schulze voting algorithm and deliberation engine.

This version was never published as a public specification. It is documented here for lineage transparency.

---

## [1.1] — 2026-01-11

### Added
- Content Safety Attestation (Amendment A)
- Temporal Claims for replay protection (Amendment B)
- Token Budget Enforcement (Amendment C)
- Canonicalization Specification (Amendment D)
- Composition Semantics (Amendment E)
- Key Lifecycle management (Amendment F)
- Version Enforcement (Amendment G)
- Fail-Closed Mandate (Amendment H)
- Revocation Resilience (Amendment I)
- Privacy Controls for audit (Amendment J)
- Size Constraints (Amendment K)
- Scope Binding (Amendment L)
- Formal Threat Model (Amendment M)
- Crypto Agility (Amendment N)
- Inter-Agent Messaging v1.2 specification
- Messaging JSON Schema

### Changed
- R-line added to CSM-1 grammar for relational context

---

## [1.0] — 2025-12-15

### Added
- Initial VCP specification with 4-layer protocol stack:
  - VCP/I (Identity): Token format, namespace tiers, encoding
  - VCP/T (Transport): Bundle format, manifests, trust anchors
  - VCP/S (Semantics): CSM-1 grammar, personas, composition
  - VCP/A (Adaptation): Context dimensions, state machine, hooks
- 4 JSON Schemas (manifest, identity token, CSM-1, adaptation context)
- Academic paper
- Newcomer guide, integration guide, adoption strategy
- MIT License