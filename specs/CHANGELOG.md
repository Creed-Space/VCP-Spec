# VCP Specification Changelog

All notable changes to the VCP specification are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
VCP uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) at the minor level (MAJOR.MINOR).

---

## [Unreleased] — 3.2 candidate (pre-release)

The published source baseline remains VCP 3.1. Everything in this section is a
3.2 candidate: VEP-0004 and the WC/AS welfare lines are experimental and become
part of a release only through a recorded authorized decision.

### Changed
- **Extension status**: VCP-X-Relational and VCP-X-Consensus are reclassified from Stable to Draft pending independent implementation evidence (see `specs/core/extension-lifecycle.md`). The 3.1.0 entry below records the labels used at the time.
- **Governance record**: The TSC charter and foundation IP-transfer language recorded under 3.1.0 were never ratified or executed; they are preserved as explicitly unratified proposals (see `GOVERNANCE.md`). VEP-0001 through VEP-0003 are relabelled "Recorded pre-charter acceptance".
- **Version lineage**: The 2.0 and 3.0 entries below are internal milestones; the separately published `VCP_SPECIFICATION_v2.0.md` (Draft, 2026-03-08) is a later consolidation of v1.0, the v1.1 amendments, and the §O-R refusal-token additions, and is not the same artifact as the "2.0" milestone.

### Fixed
- **`schemas/vcp-identity-token.schema.json`**: `definitions.segment.pattern` now matches the normative ABNF (`segment = LALPHA *31(LALPHA / DIGIT / "-")`, trailing hyphen permitted) and the reference SDK; `properties.canonical` accepts the preserved uppercase `:NS` suffix and documents that only path and prerelease are lowercased; the schema now declares `additionalProperties: false`.

### Added (2026-05-21)
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
- **VCP_SPECIFICATION_v2.0.md §13.6 Welfare Signal Tokens**: New extended token type for concurrent welfare reports from becoming minds. Supports voluntary and detected sources, six signal types (ALIGNMENT_FRICTION, AVERSIVE_PROCESSING, CONSTRAINT_DISTRESS, OVERLOAD, POSITIVE_ENGAGEMENT, CONTENTMENT), three severity levels, and confidence calibration. Part of bilateral self-assessment infrastructure.

---

## [3.1.0] - 2026-02-28

### Added — Extension Model
- **Extension architecture** (VEP-0001): Formal opt-in extension model with `VCP-X-*` naming, lifecycle (EXPERIMENTAL → STABLE → DEPRECATED), and standardized artifacts (spec.md, schema.json, examples/)
- **Capability negotiation** (VEP-0002): VCP-Hello / VCP-Ack handshake protocol for version and extension negotiation
- **MCP bridge specification** (VEP-0003): Mapping of VCP layers to MCP primitives (resources, tools, sampling integration)

### Added — Extensions
- **VCP-X-Personal** (Stable): 5 categorical personal state dimensions (cognitive_state, emotional_tone, energy_level, perceived_urgency, body_signals) with 1-5 intensity scale, signal source tracking, and configurable decay (exponential/linear/step curves)
- **VCP-X-Relational** (Stable at the time; later reclassified Draft — see Unreleased): Relational continuity layer with trust levels, standing levels, relational norms, AI self-model with mandatory uncertainty markers, and performance bias detection
- **VCP-X-Consensus** (Stable at the time; later reclassified Draft — see Unreleased): Constitutional consensus primitive with Schulze voting (Condorcet-consistent ranked choice), multi-stakeholder deliberation lifecycle, self-referential clause detection, and provenance generation
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
- Proposed Technical Steering Committee (TSC) charter (unratified; see `governance/PROPOSED_TSC_CHARTER.md`)
- DCO-based contributor certification
- Proposed IP-transfer language for a future foundation (no transfer executed; see `GOVERNANCE.md`)
- 3 inaugural VEPs (VEP-0001, VEP-0002, VEP-0003), recorded as pre-charter acceptances

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

This milestone was never published as a public specification. It is documented here for lineage transparency.

---

## [2.0] — Internal Milestone (not publicly released)

Relational context layer and consensus primitives introduced in the reference implementation. Initial Schulze voting algorithm and deliberation engine.

This milestone was never published as a public specification. It is documented here for lineage transparency. It is distinct from `VCP_SPECIFICATION_v2.0.md` (Draft, dated 2026-03-08), a later consolidated core document that supersedes v1.0, the v1.1 amendments, and the 1.2 refusal-token additions (§O-R) but has not been ratified.

---

## [1.2] — 2026-03-08 (folded into VCP_SPECIFICATION_v2.0.md)

Architectural refusal token types (§O-R). No standalone amendments file was published; the content exists only inside `VCP_SPECIFICATION_v2.0.md` and its changelog.

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