# VCP Specification Changelog

All notable changes to the VCP specification are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
VCP uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) at the minor level (MAJOR.MINOR).

---

## [3.1] — 2026-02-28

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
