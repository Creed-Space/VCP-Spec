# Value-Context Protocol (VCP) Specification v3.1

**Version**: 3.1
**Date**: 2026-02-28
**Status**: Stable
**Authors**: Nell Watson, Elena Ajayi, Filip Alimpić, Awwab Mahdi, Blake Wells, Claude (Anthropic)

---

## Abstract

The Value-Context Protocol (VCP) is an open specification for transporting constitutional values, behavioral rules, and personal context to AI systems. Version 3.1 introduces a formal extension model, capability negotiation, and five protocol extensions for personal state, relational context, consensus voting, session handoff, and intent inference.

---

## 1. Protocol Overview

VCP is a six-layer protocol stack — **I-T-S-A-M-E** ("It's-a me!"):

```
┌─────────────────────────────────────────────────────────────────────┐
│  Layer 6 — VCP/E  ECONOMIC GOVERNANCE                              │
│  WHO PAYS and transaction governance                                │
│  Fiduciary constraints · Authorization gaps · Capability decisions  │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 5 — VCP/M  MESSAGING                                        │
│  WHO TALKS - Inter-agent message exchange                           │
│  Message types · Escalation severity · Delivery semantics           │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 4 — VCP/A  ADAPTATION                                       │
│  WHEN and HOW constitutions apply                                   │
│  Context encoding · State tracking · Messaging · Deterministic hooks│
├─────────────────────────────────────────────────────────────────────┤
│  Layer 3 — VCP/S  SEMANTICS                                        │
│  WHAT the values mean                                               │
│  CSM-1 grammar · Persona composition · Traits · Personal state      │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 2 — VCP/T  TRANSPORT                                        │
│  HOW integrity and provenance travel                                │
│  Signed bundles · Hash verification · Audit logging                 │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 1 — VCP/I  IDENTITY                                         │
│  WHO and WHAT is being addressed                                    │
│  Naming · Namespaces · Registry · Encoding                          │
├─────────────────────────────────────────────────────────────────────┤
│                   Core Security                                     │
│  Encryption | Scanning | Opacity | Revocation | Audit               │
├─────────────────────────────────────────────────────────────────────┤
│                   Extensions (VCP-X-*)                              │
│  Personal | Relational | Consensus | Torch | Intent                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.1. Design Principles

1. **Portability**: Define context once, transport it everywhere
2. **Adaptation**: Context profiles shift by situation
3. **Liveness**: Real-time personal state modulates AI behavior
4. **Verification**: Cryptographic integrity and provenance
5. **Privacy**: Minimize source disclosure through purpose-limited derived context; deployment privacy remains an application obligation
6. **Extensibility**: Core is stable; extensions are opt-in

### 1.2. What's New in v3.1

| Feature | Type | Specification |
|---------|------|--------------|
| Extension model | Core | [VEP-0001](../veps/VEP-0001-extension-model.md) |
| Capability negotiation | Core | [specs/core/capability-negotiation.md](./core/capability-negotiation.md) |
| MCP bridge | Core | [specs/core/mcp-bridge.md](./core/mcp-bridge.md) |
| Context encryption | Core | [specs/core/security.md §1](./core/security.md) |
| Injection scanning | Core | [specs/core/security.md §2](./core/security.md) |
| Context opacity | Core | [specs/core/security.md §3](./core/security.md) |
| Revocation infrastructure | Core | [specs/core/security.md §4](./core/security.md) |
| Tamper-evident audit | Core | [specs/core/audit.md](./core/audit.md) |
| Personal state | Extension | [VCP-X-Personal](./extensions/VCP-X-Personal/spec.md) |
| Relational continuity | Extension | [VCP-X-Relational](./extensions/VCP-X-Relational/spec.md) |
| Constitutional consensus | Extension | [VCP-X-Consensus](./extensions/VCP-X-Consensus/spec.md) |
| Session handoff | Extension | [VCP-X-Torch](./extensions/VCP-X-Torch/spec.md) |
| Intent inference | Extension | [VCP-X-Intent](./extensions/VCP-X-Intent/spec.md) |

---

## 2. Core Protocol Layers

The six layers of the VCP stack. Layers 1–4 are unchanged from v1.0; layers 5–6 were introduced in v2.0.

### 2.1. VCP/I — Identity

Defines token format, namespace tiers (personal, organizational, platform), and identity encoding. See [Identity documentation](../docs/identity/).

### 2.2. VCP/T — Transport

Defines the signed bundle format: manifests, content hashes, trust anchors, and signature verification. See [v1.0 SS6](./VCP_SPECIFICATION_v1.0.md).

### 2.3. VCP/S — Semantics

Defines CSM-1 grammar for constitutional profile encoding, persona profiles, and composition semantics. See [CSM-1 Grammar](../docs/content/CSM1_GRAMMAR_SPECIFICATION.md).

### 2.4. VCP/A — Adaptation

Defines context dimensions, state machine, hooks, and context specification. See [Adaptation documentation](../docs/adaptation/).

### 2.5. VCP/M — Messaging

Defines inter-agent message types, escalation severity levels, and delivery semantics. See [Messaging specification](./VCP_MESSAGING_v2.0.md).

### 2.6. VCP/E — Economic Governance

Defines fiduciary constraints, authorization gaps (capability, accountability, compatibility), and transaction governance. See [Economic Governance specification](./VCP_ECONOMIC_GOVERNANCE_v2.0.md).

---

## 3. Core Security (v3.1 additions)

Full specification: [specs/core/security.md](./core/security.md)

### 3.1. Context Encryption
The v3.1 security profile specifies Fernet symmetric encryption for personal context at rest. Conforming production and staging implementations MUST activate the selected at-rest protection and fail closed on decryption errors. This requirement does not protect plaintext after authorized decryption or data sent to downstream services.

### 3.2. Injection Scanning
The reference profile defines 12 detection patterns (8 OWASP, 2 VCP-specific, 2 Unicode) as one defense-in-depth control before model use. Passing these patterns does not establish that content is safe from prompt injection. Applications MUST combine verification, parsing, policy, least privilege, output controls, and adversarial tests appropriate to the deployment.

### 3.3. Context Opacity
Protection levels (STANDARD, ELEVATED, HIGH, CRITICAL) may be computed from personal-state inputs. A conforming opacity integration MUST prevent raw personal signals from reaching inference models and expose only the approved derived level. Derived levels can still reveal sensitive state and require consent, minimisation, access control, retention limits, and inference review. Conformance requires end-to-end mediation evidence rather than an encoder claim alone.

### 3.4. Revocation Infrastructure
CRL (Certificate Revocation List) + OCSP-style stapled proofs. Signature verification via Ed25519 (preferred) or HMAC-SHA256. Fail-closed: if all revocation sources are unavailable, treat as revoked.

---

## 4. Core Verification (v3.1 additions)

Full specification: [specs/core/audit.md](./core/audit.md)

### 4.1. Tamper-Evident Audit Chain
The profile specifies a SHA-256 hash chain with canonical JSON serialization and serialized appends. Truncated hashes may reduce stored detail but are not anonymization: stable or low-entropy inputs can remain linkable. Audit designs MUST separately address minimisation, keyed pseudonymization where appropriate, access, retention, erasure obligations, and chain verification.

---

## 5. Capability Negotiation (v3.1 addition)

Full specification: [specs/core/capability-negotiation.md](./core/capability-negotiation.md)

Clients and servers negotiate VCP version and active extensions via VCP-Hello / VCP-Ack handshake. Legacy VCP 1.0 clients are supported via 5-second timeout fallback.

---

## 6. Extension Model (v3.1 addition)

Full specification: [specs/extensions/README.md](./extensions/README.md)

Extensions follow the `VCP-X-{Name}` naming pattern. Each registered extension provides a specification and schema; examples, reference implementations, and conformance coverage are tracked separately and MUST NOT be inferred from registration. Extensions are opt-in and negotiated per session.

### 6.1. Current Extensions

| Extension | Status | Description | Spec |
|-----------|--------|-------------|------|
| VCP-X-Personal | Stable | Personal state (5 dims + intensity + decay) | [spec](./extensions/VCP-X-Personal/spec.md) |
| VCP-X-Relational | Draft | Relational continuity (trust, standing, norms, self-model) | [spec](./extensions/VCP-X-Relational/spec.md) |
| VCP-X-Consensus | Draft | Constitutional consensus (Schulze voting + deliberation) | [spec](./extensions/VCP-X-Consensus/spec.md) |
| VCP-X-Torch | Stable | Session handoff between agents | [spec](./extensions/VCP-X-Torch/spec.md) |
| VCP-X-Intent | Experimental | Heuristic intent inference | [spec](./extensions/VCP-X-Intent/spec.md) |

---

## 7. MCP Bridge (v3.1 addition)

Full specification: [specs/core/mcp-bridge.md](./core/mcp-bridge.md)

VCP layers map to MCP primitives: bundles as resources, operations as tools, context via sampling integration. Capability negotiation piggybacks on MCP's `initialize` handshake.

---

## 8. Wire Format Examples

Annotated walkthroughs demonstrating VCP operations end-to-end:

| Example | Features Demonstrated |
|---------|----------------------|
| [CSM-1 Encode/Decode](./examples/csm1-encode-decode.md) | Token lifecycle, signing, verification, LLM injection |
| [Personal State Roundtrip](./examples/personal-state-roundtrip.md) | Signal encoding, decay math, lifecycle states, engagement reset |
| [Consensus Deliberation](./examples/consensus-deliberation.md) | Multi-stakeholder voting, Schulze algorithm, provenance |
| [Capability Handshake](./examples/capability-handshake.md) | Version negotiation, extension discovery, MCP integration |

---

## 9. JSON Schemas

| Schema | Validates | New in v3.1 |
|--------|----------|-------------|
| [vcp-manifest-v1](../schemas/vcp-manifest-v1.schema.json) | Signed bundle manifests | No |
| [vcp-identity-token](../schemas/vcp-identity-token.schema.json) | Identity tokens | No |
| [vcp-semantics-csm1](../schemas/vcp-semantics-csm1.schema.json) | CSM-1 compact tokens | No |
| [vcp-adaptation-context](../schemas/vcp-adaptation-context.schema.json) | Adaptation context | No |
| [vcp-messaging-v1.2](../schemas/vcp-messaging-v1.2.schema.json) | Inter-agent messaging | No |
| [vcp-capability-handshake](../schemas/vcp-capability-handshake.schema.json) | Capability negotiation | **Yes** |

Extension schemas are co-located with their specifications in `specs/extensions/VCP-X-*/schema.json`.

---

## 10. Versioning

VCP uses semantic versioning at the minor level. Version history:

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2025-12-15 | Initial specification |
| 1.1 | 2026-01-11 | Security amendments, inter-agent messaging |
| 2.0 | Internal | Relational context, consensus (reference implementation only) |
| 3.0 | Internal | Personal state with float signals (reference implementation only) |
| 3.1 | 2026-02-28 | Extension model, capability negotiation, 5 extensions, core security |

Versions 2.0 and 3.0 shipped in the reference implementation before the public specification caught up. They are documented in the [CHANGELOG](./CHANGELOG.md) for lineage transparency.

---

## 11. Conformance

### 11.1. Conformance Levels

| Level | Requirements |
|-------|-------------|
| **Core** | Implement VCP/I, VCP/T, VCP/S, VCP/A |
| **Core + Security** | Core + context encryption + injection scanning + revocation |
| **Core + Messaging** | Core + Security + VCP/M messaging + VCP/E economic governance |
| **Full** | Core + Security + Messaging + capability negotiation + all stable extensions |

### 11.2. Extension Conformance

Each extension defines its own conformance requirements in its spec.md. Implementations MAY support any subset of extensions.

---

## 12. References

- [VCP v1.0 Specification](./VCP_SPECIFICATION_v1.0.md)
- [VCP v1.1 Amendments](./VCP_SPECIFICATION_v1.1_AMENDMENTS.md)
- [VCP Academic Paper](./value_context_protocols_paper_v1.md)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Schulze Method (Wikipedia)](https://en.wikipedia.org/wiki/Schulze_method)
- [RFC 2119: Key words for use in RFCs](https://www.rfc-editor.org/rfc/rfc2119)
- [Fernet Specification](https://github.com/fernet/spec/blob/master/Spec.md)
- [Ed25519 (RFC 8032)](https://www.rfc-editor.org/rfc/rfc8032)

---

## Authors

Nell Watson, Elena Ajayi, Filip Alimpić, Awwab Mahdi, Blake Wells, Claude (Anthropic)

A **[Creed Space](https://creedspace.com)** project. Possible future foundation
stewardship remains unapproved and no transfer is currently claimed.

---

*Context that travels with you.*
