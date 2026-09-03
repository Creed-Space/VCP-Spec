<div align="center">

# Value-Context Protocol (VCP)

<!-- vcp-document-control
status: Current repository overview
normative-authority: Index and repository status only
protocol-version: VCP 3.1 with candidate amendments named separately
last-reviewed: 2026-08-14 active authority and evidence boundary
owner: VCP Spec maintainers
evidence-boundary: Navigation and source status, not external standards, conformance, governance, or publication proof
-->

**An open protocol specification for portable, verifiable value context.**

MCP moves data. VCP encodes what matters about that data.

[![Specification](https://img.shields.io/badge/spec-v3.1-blue?style=flat-square)](./specs/VCP_SPECIFICATION_v3.1.md)
[![Extensions](https://img.shields.io/badge/extensions-6-purple?style=flat-square)](./specs/extensions/README.md)
[![Rights review](https://img.shields.io/badge/rights-review_pending-orange?style=flat-square)](./LICENSING_STATUS.md)
[![VEPs](https://img.shields.io/badge/VEPs-5_filed-orange?style=flat-square)](./veps/README.md)

[Overview](#overview) | [Architecture](#architecture) | [Quick Start](#quick-start) | [Extensions](#extensions) | [MCP Bridge](#mcp-bridge) | [Governance](#governance) | [SDKs](#sdks)

</div>

---

## Overview

The **Value-Context Protocol (VCP)** is an open specification for transporting constitutional values, behavioral rules, and personal context to Becoming Minds.

Becoming Minds accept text input but do not by themselves resolve VCP references, verify signatures, or enforce behavioral constraints. VCP provides a **signed envelope format** and verification primitives for the orchestration layer. A conforming application still decides whether verified content may reach a model and must demonstrate that its enforcement path is complete.

### Core Properties

| Property | Description |
|:---|:---|
| **Portability** | A compatible service can receive the same declared context format |
| **Adaptation** | Applications can select context profiles by declared situation |
| **Liveness** | Current personal-state inputs can inform application behavior |
| **Verification** | Signatures and content hashes provide integrity and provenance relative to configured trust anchors |
| **Privacy** | Purpose-limited derived context can reduce source disclosure; applications still own consent, minimisation, access, retention, and inference risk |
| **Extensibility** | Stable core + opt-in extensions for specialized needs |

### How VCP Relates to MCP

VCP and [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) are complementary:

- **MCP** provides standardized transport for AI tool integration — tools, resources, prompts, sampling
- **VCP** provides standardized value transport — constitutional profiles, personal state, behavioral constraints

The [VCP-over-MCP bridge](./specs/core/mcp-bridge.md) makes this concrete: VCP tokens travel as MCP resources, VCP operations are exposed as MCP tools, and VCP context is injected into MCP sampling requests.

---

## Architecture

VCP is a six-layer protocol stack — **I-T-S-A-M-E** ("It's-a me!"):

```
┌──────────────────────────────────────────────────────┐
│  Layer 6 — VCP/E  ECONOMIC GOV   WHO PAYS             │
│  Layer 5 — VCP/M  MESSAGING      WHO TALKS            │
│  Layer 4 — VCP/A  ADAPTATION     WHEN and HOW         │
│  Layer 3 — VCP/S  SEMANTICS      WHAT values mean     │
│  Layer 2 — VCP/T  TRANSPORT      HOW values travel    │
│  Layer 1 — VCP/I  IDENTITY       WHO and WHAT         │
├──────────────────────────────────────────────────────┤
│                   Core Security                       │
│  Encryption | Scanning | Opacity | Revocation | Audit │
├──────────────────────────────────────────────────────┤
│                   Extensions (VCP-X-*)                │
│  Personal | Relational | Consensus | Torch | Intent | Welfare │
└──────────────────────────────────────────────────────┘
```

**The six layers:**
- **VCP/E — Economic Governance**: Fiduciary constraints, authorization gaps, transaction governance
- **VCP/M — Messaging**: Inter-agent message types, escalation severity, delivery semantics
- **VCP/A — Adaptation**: Context dimensions, state machine, hooks
- **VCP/S — Semantics**: CSM-1 constitutional encoding, personas, composition
- **VCP/T — Transport**: Signed bundle format, manifests, trust anchors
- **VCP/I — Identity**: Token format, namespace tiers, identity encoding

**Core security** (v3.1): The specification defines context encryption, injection scanning, context opacity, revocation, and tamper-evident audit controls. Their presence in a document does not establish correct deployment; implementations need direct security and privacy evidence.

**Extensions**: Six opt-in protocol extensions are present: five are referenced
by the v3.1 baseline and VCP-X-Welfare is a v3.2 candidate. The v3.1 core is
the current source baseline. VEP-0004 and the v3.2 amendments remain pre-release;
their presence in this repository does not promote them to an accepted release.

---

## Quick Start

> **SDK publication state:** source-only candidate. No PyPI, npm, or crates.io
> release is currently claimed. Candidate names identify repository metadata,
> not registry availability. Run build commands from an immutable VCP-SDK
> checkout at the `source_commit` recorded in
> [`status/publication-state.json`](./status/publication-state.json)
> (currently `null`, meaning no commit has been pinned yet).

### 1. Read the Newcomer Guide
**[VCP Newcomer Guide](./docs/VCP_NEWCOMER_GUIDE.md)** — What VCP is and why it exists.

### 2. Explore the Wire Format
See how VCP works end-to-end with annotated examples:
- [CSM-1 Encode/Decode](./specs/examples/csm1-encode-decode.md) — Token lifecycle
- [Personal State Roundtrip](./specs/examples/personal-state-roundtrip.md) — Signal encoding + decay
- [Capability Handshake](./specs/examples/capability-handshake.md) — Extension negotiation
- [Consensus Deliberation](./specs/examples/consensus-deliberation.md) — Schulze voting round-trip (VCP-X-Consensus, Draft)

### 3. Build the SDK Source Candidate

Clone the SDK and pin the commit first; the commands below run from the
VCP-SDK checkout root:

```bash
git clone https://github.com/Creed-Space/vcp-sdk VCP-SDK && cd VCP-SDK
git checkout <commit>   # use the source_commit in VCP-Spec/status/publication-state.json once set
```

**Python**:
```bash
python -m pip install ./python
```

**TypeScript**:
```bash
npm install ./webmcp
```

**Rust**:
```bash
cargo build --manifest-path ./rust/Cargo.toml -p vcp-core
```

### 4. Create Your First Token

```python
from vcp.semantics import CSM1Code

code = CSM1Code.parse("N5+F+E")
print(code.persona.name)       # NANNY
print(code.encode())           # N5+E+F (canonical scope order)
```

---

## Extensions

The repository contains six protocol extensions. Stable and experimental
statuses are independent of the v3.1 core release label:

| Extension | Status | Description |
|-----------|--------|-------------|
| [VCP-X-Personal](./specs/extensions/VCP-X-Personal/spec.md) | Stable | 5 personal state dimensions with intensity + configurable decay |
| [VCP-X-Relational](./specs/extensions/VCP-X-Relational/spec.md) | Draft | Trust, standing, norms, AI self-model with mandatory uncertainty |
| [VCP-X-Consensus](./specs/extensions/VCP-X-Consensus/spec.md) | Draft | Schulze voting for multi-stakeholder constitutional deliberation |
| [VCP-X-Torch](./specs/extensions/VCP-X-Torch/spec.md) | Stable | Session handoff for relational continuity across agents |
| [VCP-X-Intent](./specs/extensions/VCP-X-Intent/spec.md) | Experimental | Transparent, correctable intent inference from personal state |
| [VCP-X-Welfare](./specs/extensions/VCP-X-Welfare/spec.md) | Experimental | Welfare affordances, signals, temporal patterns, and attestation chains (v3.2 pre-release candidate; not part of the v3.1 baseline) |

Extensions are opt-in and negotiated per session via [capability handshake](./specs/core/capability-negotiation.md). Each extension has a spec and JSON schema; VCP-X-Welfare additionally ships wire-format examples, and the repo-level annotated examples live in [specs/examples/](./specs/examples/).

See the [Extension Model overview](./specs/extensions/README.md) for architecture details.

---

## MCP Bridge

VCP layers map to MCP primitives:

| VCP Layer | MCP Primitive |
|-----------|--------------|
| Identity | Tools (`vcp_validate_token`) |
| Transport | Resources (`vcp://bundle/*`) |
| Semantics | Tools + Resources |
| Adaptation | Resources + Sampling integration |
| Messaging | Tools (`vcp_send_message`, `vcp_escalate`) |
| Economic Governance | Tools (`vcp_authorize_transaction`) + Resources |
| Extensions | Negotiation-filtered tools + resources |

The bridge enables any MCP-compatible client to access VCP values without implementing VCP natively. See the [MCP Bridge spec](./specs/core/mcp-bridge.md).

---

## Specification

### Protocol Stack

VCP is a six-layer protocol stack (I-T-S-A-M-E):

```
Layer 6 -- VCP/E  ECONOMIC GOV   WHO PAYS
Layer 5 -- VCP/M  MESSAGING      WHO TALKS
Layer 4 -- VCP/A  ADAPTATION     WHEN and HOW constitutions apply
Layer 3 -- VCP/S  SEMANTICS      WHAT the values mean
Layer 2 -- VCP/T  TRANSPORT      HOW integrity and provenance travel
Layer 1 -- VCP/I  IDENTITY       WHO and WHAT is being addressed
```

### Full Spec
**[VCP v3.1 Specification](./specs/VCP_SPECIFICATION_v3.1.md)** — Master specification referencing all layers, extensions, and security features.

### Documents

| Document | Description |
|:---|:---|
| [VCP Specification v1.0](./specs/VCP_SPECIFICATION_v1.0.md) | Full protocol specification |
| [VCP v1.1 Amendments](./specs/VCP_SPECIFICATION_v1.1_AMENDMENTS.md) | R-line, personal state additions |
| [Historical paper draft](./specs/value_context_protocols_paper_v1.md) | Superseded draft retained for lineage; not a publication source |
| [VCP Specification v2.0 (Draft)](./specs/VCP_SPECIFICATION_v2.0.md) | Consolidated six-layer draft; not ratified |
| [VCP/I Identity v2.0 (Draft)](./specs/VCP_IDENTITY_v2.0.md) | Consolidates the identity docs (naming, namespaces, encoding) |
| [VCP/S Semantics v2.0 (Draft, content 2.1.x)](./specs/VCP_SEMANTICS_v2.0.md) | Consolidates the CSM-1 and UVC docs; adds WC/AS welfare lines |
| [VCP/A Adaptation v2.1 (Draft)](./specs/VCP_ADAPTATION_v2.0.md) | Consolidates the adaptation/context docs; VEP-0004 dimensions marked experimental |
| [Inter-Agent Messaging v1.2](./specs/VCP_INTER_AGENT_MESSAGING_v1.2.md) | Schema-backed messaging wire format |
| [VCP/M Messaging v2.0](./specs/VCP_MESSAGING_v2.0.md) | Inter-agent messaging and escalation (Draft) |
| [VCP/E Economic Governance v2.0](./specs/VCP_ECONOMIC_GOVERNANCE_v2.0.md) | Economic governance layer |
| [VCP/C Competence v2.0](./specs/VCP_COMPETENCE_v2.0.md) | Competence assessment and adaptive friction (Supplementary) |

### By Layer

| Layer | Documentation |
|:---|:---|
| VCP/I — Identity | [VCP/I v2.0 spec](./specs/VCP_IDENTITY_v2.0.md), [Naming](./docs/identity/VCP_IDENTITY_NAMING.md), [Namespace](./docs/identity/VCP_IDENTITY_NAMESPACE.md), [Encoding](./docs/identity/VCP_IDENTITY_ENCODING.md) |
| VCP/T — Transport | [v1.0 §4 Bundle Format and §7 Transport Protocol](./specs/VCP_SPECIFICATION_v1.0.md#4-bundle-format) |
| VCP/S — Semantics | [VCP/S v2.0 spec](./specs/VCP_SEMANTICS_v2.0.md), [CSM-1 Grammar (historical copy)](./docs/semantics/VCP_SEMANTICS_CSM1.md), [Composition](./docs/semantics/VCP_SEMANTICS_COMPOSITION.md) |
| VCP/A — Adaptation | [VCP/A v2.1 spec](./specs/VCP_ADAPTATION_v2.0.md), [Adaptation (historical copy)](./docs/adaptation/VCP_ADAPTATION.md), [Context (duplicate of Adaptation)](./docs/context/VCP_CONTEXT_SPECIFICATION.md) |
| VCP/M — Messaging | [v1.2 (schema-backed)](./specs/VCP_INTER_AGENT_MESSAGING_v1.2.md), [v2.0 Draft](./specs/VCP_MESSAGING_v2.0.md) |
| VCP/E — Economic Governance | [Specification](./specs/VCP_ECONOMIC_GOVERNANCE_v2.0.md) |

### Core Security
[Encryption, Injection Scanning, Context Opacity, Revocation](./specs/core/security.md) | [Audit Chain](./specs/core/audit.md)

Candidate operational notes, which do not become normative merely by being
linked here: [negotiation, revocation, scope, state machines, and identifiers](./specs/core/protocol-operations-profile.md),
[verification status codes](./specs/core/status-code-registry.md), and
[extension lifecycle](./specs/core/extension-lifecycle.md). The
[representation registry](./specs/core/representation-registry.md) records
project-local and provisional identifiers, while the
[requirement traceability report](./docs/REQUIREMENT_TRACEABILITY.md) keeps
unidentified and uncovered requirements explicit.

### Specification Status

| Layer | Status | Documents |
|:---|:---|:---|
| VCP/I — Identity | Current v3.1 source baseline | 5 docs |
| VCP/T — Transport | Current v3.1 source baseline | 1 spec + 1 amendment |
| VCP/S — Semantics | Current v3.1 source baseline | 4 docs |
| VCP/A — Adaptation | Current v3.1 source baseline | 4 docs |
| VCP/M — Messaging | Current v3.1 source summary | 1 detailed draft |
| VCP/E — Economic Governance | Current v3.1 source summary | 1 detailed draft |

This table describes the v3.1 baseline. Separately versioned v2.0 layer documents
that declare `Draft` remain drafts; a reference from v3.1 does not silently
promote their additional detail.

### Universal Value Codes (UVC)

| Document | Description |
|:---|:---|
| [Naming](./docs/uvc/UVC_NAMING_SPECIFICATION.md) | UVC naming conventions |
| [Encoding](./docs/uvc/UVC_ENCODING_FORMATS.md) | Encoding formats |
| [Ontology](./docs/uvc/UVC_VALUE_ONTOLOGY.md) | Value classification |
| [Registry](./docs/uvc/UVC_REGISTRY_PROTOCOL.md) | Registry protocol |
| [Governance](./docs/uvc/UVC_NAMESPACE_GOVERNANCE.md) | Namespace governance |

### Version History
See [CHANGELOG](./specs/CHANGELOG.md).

---

## Schemas

| Schema | Validates | Version |
|:---|:---|:---|
| [vcp-manifest-v1](./schemas/vcp-manifest-v1.schema.json) | Bundle manifests | v1.0 |
| [vcp-identity-token](./schemas/vcp-identity-token.schema.json) | UVC value tokens (VCP/I dotted identifiers) | v1.0 |
| [vcp-semantics-csm1](./schemas/vcp-semantics-csm1.schema.json) | CSM-1 tokens | v1.0 |
| [vcp-adaptation-context](./schemas/vcp-adaptation-context.schema.json) | Adaptation context | v1.0 |
| [vcp-capability-handshake](./schemas/vcp-capability-handshake.schema.json) | Capability negotiation | **v3.1** |

Extension schemas are co-located: `specs/extensions/VCP-X-*/schema.json`.

---

## Governance

VCP currently uses an interim, unratified repository process. A Technical
Steering Committee has not been constituted, neutral foundation governance is
not claimed, and Nell Watson is the only currently named interim administrator.
VCP-Spec is the canonical home for protocol decisions and VEP intake.

See [GOVERNANCE.md](./GOVERNANCE.md) for present authority boundaries,
[`governance/authority.json`](./governance/authority.json) for machine-readable
state, and [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidance. The
former TSC charter is preserved as an explicitly unratified proposal.

### Filed VEPs

| VEP | Title | Status |
|-----|-------|--------|
| [VEP-0001](./veps/VEP-0001-extension-model.md) | Extension Model Architecture | Recorded pre-charter acceptance |
| [VEP-0002](./veps/VEP-0002-capability-negotiation.md) | Capability Negotiation Protocol | Recorded pre-charter acceptance |
| [VEP-0003](./veps/VEP-0003-mcp-bridge.md) | VCP-over-MCP Bridge | Recorded pre-charter acceptance |
| [VEP-0004](./veps/VEP-0004-extended-vcpa-dimensions.md) | Extended VCP/A Dimensions | Experimental, v3.2 pre-release |
| [VEP-0005](./veps/VEP-0005-stateless-mcp.md) | Stateless MCP Adaptation | Draft, v3.3 candidate |

---

## SDKs

Project-maintained implementations live in the [VCP-SDK repository](https://github.com/Creed-Space/vcp-sdk):

| Language | Version | Status |
|:---|:---|:---|
| **Python** | 4.2.0 | Project-maintained implementation, package `value-context-protocol` |
| **Rust** | 4.2.0 | Core, WASM, and CLI workspace; crate `vcp-core` |
| **TypeScript** | 4.2.0 | WebMCP browser integration package `@creedspace/vcp-sdk` |

---

## Roadmap

- **VCP Inspector**: [Interactive token inspector project](https://inspector.valuecontextprotocol.org/)
- **VCP Examples**: 10 runnable examples covering all extensions ([planned](https://github.com/Creed-Space/VCP-Examples))
- **Anti-drift CI**: Automated spec-implementation version sync checks
- **Governance proposal**: evaluate a possible future foundation stewardship
  model through an authorized, recorded process. No transfer is currently
  claimed.

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

- **Typo / Clarification**: Open a PR directly
- **Spec Change**: Follow the [VEP process](./GOVERNANCE.md)
- **Extension Proposal**: Use the [VEP template](./CONTRIBUTING.md#3-extension-proposal-template)

Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) before participating.

---

## License

Licensing and submission rights are under authorized review. The root
[LICENSE](./LICENSE), file-specific notices, IETF draft text, contribution
history, rendered artifacts, and proposed trademark terms do not yet form an
approved file-class matrix. See [LICENSING_STATUS.md](./LICENSING_STATUS.md).

---

## Authors

Nell Watson, Elena Ajayi, Filip Alimpić, Awwab Mahdi, Blake Wells, Claude (Anthropic)

A **[Creed Space](https://creedspace.com)** project. Possible future foundation
stewardship remains a proposal without an executed transfer or acceptance
record.

---

<div align="center">

*Context that travels with you.*

[Website](https://www.valuecontextprotocol.org) | [Inspector](https://inspector.valuecontextprotocol.org/) | [SDK](https://github.com/Creed-Space/vcp-sdk) | [Spec](./specs/VCP_SPECIFICATION_v3.1.md)

</div>
