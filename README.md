<div align="center">

# Value-Context Protocol (VCP)

**The open standard for encoding values in AI context.**

MCP moves data. VCP encodes what matters about that data.

[![Specification](https://img.shields.io/badge/spec-v3.1-blue?style=flat-square)](./specs/VCP_SPECIFICATION_v3.1.md)
[![Extensions](https://img.shields.io/badge/extensions-5-purple?style=flat-square)](./specs/extensions/README.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](./LICENSE)
[![VEPs](https://img.shields.io/badge/VEPs-3_filed-orange?style=flat-square)](./veps/)

[Overview](#overview) | [Architecture](#architecture) | [Quick Start](#quick-start) | [Extensions](#extensions) | [MCP Bridge](#mcp-bridge) | [Governance](#governance) | [SDKs](#sdks)

</div>

---

## Overview

The **Value-Context Protocol (VCP)** is an open specification for transporting constitutional values, behavioral rules, and personal context to AI systems.

AI systems accept text input but have no native ability to resolve references, verify signatures, or validate behavioral constraints. VCP provides a **signed envelope format** with cryptographic verification at the orchestration layer, delivering complete, self-contained behavioral context to the model.

### Core Properties

| Property | Description |
|:---|:---|
| **Portability** | Define your context once — every compatible service receives it |
| **Adaptation** | Context profiles shift by situation: work mode, personal mode, crisis mode |
| **Liveness** | Real-time personal state (energy, focus, urgency) modulates AI behavior |
| **Verification** | Cryptographic signatures and content hashes ensure integrity |
| **Privacy** | Share *influence* without sharing *information* |
| **Extensibility** | Stable core + opt-in extensions for specialized needs |

### How VCP Relates to MCP

VCP and [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) are complementary:

- **MCP** provides standardized transport for AI tool integration — tools, resources, prompts, sampling
- **VCP** provides standardized value transport — constitutional profiles, personal state, behavioral constraints

The [VCP-over-MCP bridge](./specs/core/mcp-bridge.md) makes this concrete: VCP tokens travel as MCP resources, VCP operations are exposed as MCP tools, and VCP context is injected into MCP sampling requests.

---

## Architecture

VCP is a four-layer protocol stack with an extension model:

```
┌──────────────────────────────────────────────────────┐
│                   Extensions (VCP-X-*)                │
│  Personal | Relational | Consensus | Torch | Intent  │
├──────────────────────────────────────────────────────┤
│  Layer 4 — VCP/A  ADAPTATION     WHEN and HOW        │
│  Layer 3 — VCP/S  SEMANTICS      WHAT values mean    │
│  Layer 2 — VCP/T  TRANSPORT      HOW values travel   │
│  Layer 1 — VCP/I  IDENTITY       WHO and WHAT        │
├──────────────────────────────────────────────────────┤
│                   Core Security                       │
│  Encryption | Scanning | Opacity | Revocation | Audit │
└──────────────────────────────────────────────────────┘
```

**Core layers** (stable since v1.0):
- **VCP/I — Identity**: Token format, namespace tiers, identity encoding
- **VCP/T — Transport**: Signed bundle format, manifests, trust anchors
- **VCP/S — Semantics**: CSM-1 constitutional encoding, personas, composition
- **VCP/A — Adaptation**: Context dimensions, state machine, hooks

**Core security** (v3.1): Context encryption, injection scanning, context opacity, revocation infrastructure, tamper-evident audit chain.

**Extensions** (v3.1): Opt-in protocol extensions negotiated per session via capability handshake.

---

## Quick Start

### 1. Read the Newcomer Guide
**[VCP Newcomer Guide](./docs/VCP_NEWCOMER_GUIDE.md)** — What VCP is and why it exists.

### 2. Explore the Wire Format
See how VCP works end-to-end with annotated examples:
- [CSM-1 Encode/Decode](./specs/examples/csm1-encode-decode.md) — Token lifecycle
- [Personal State Roundtrip](./specs/examples/personal-state-roundtrip.md) — Signal encoding + decay
- [Capability Handshake](./specs/examples/capability-handshake.md) — Extension negotiation

### 3. Install the SDK

**Python**:
```bash
pip install creed-sdk
```

**TypeScript**:
```bash
npm install @creed-space/vcp-sdk
```

**Rust**:
```toml
[dependencies]
vcp-sdk = "3.1"
```

### 4. Create Your First Token

```python
from creed_sdk import VCPClient

client = VCPClient()
token = client.create_token(
    persona="supportive_companion",
    dimensions={"empathy": "high", "transparency": "high"},
    scope={"domain": "mental_health"}
)
print(token.csm1)  # csm1:supportive_companion:EH-TH-...
```

---

## Extensions

VCP v3.1 introduces five protocol extensions:

| Extension | Status | Description |
|-----------|--------|-------------|
| [VCP-X-Personal](./specs/extensions/VCP-X-Personal/spec.md) | Stable | 5 personal state dimensions with intensity + configurable decay |
| [VCP-X-Relational](./specs/extensions/VCP-X-Relational/spec.md) | Stable | Trust, standing, norms, AI self-model with mandatory uncertainty |
| [VCP-X-Consensus](./specs/extensions/VCP-X-Consensus/spec.md) | Stable | Schulze voting for multi-stakeholder constitutional deliberation |
| [VCP-X-Torch](./specs/extensions/VCP-X-Torch/spec.md) | Stable | Session handoff for relational continuity across agents |
| [VCP-X-Intent](./specs/extensions/VCP-X-Intent/spec.md) | Experimental | Transparent, correctable intent inference from personal state |

Extensions are opt-in and negotiated per session via [capability handshake](./specs/core/capability-negotiation.md). Each extension has a spec, JSON schema, and wire format examples.

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
| Extensions | Negotiation-filtered tools + resources |

The bridge enables any MCP-compatible client to access VCP values without implementing VCP natively. See the [MCP Bridge spec](./specs/core/mcp-bridge.md).

---

## Specification

### Full Spec
**[VCP v3.1 Specification](./specs/VCP_SPECIFICATION_v3.1.md)** — Master specification referencing all layers, extensions, and security features.

### By Layer

| Layer | Documentation |
|:---|:---|
| VCP/I — Identity | [Naming](./docs/identity/VCP_IDENTITY_NAMING.md), [Namespace](./docs/identity/VCP_IDENTITY_NAMESPACE.md), [Encoding](./docs/identity/VCP_IDENTITY_ENCODING.md) |
| VCP/T — Transport | [v1.0 Spec SS6](./specs/VCP_SPECIFICATION_v1.0.md) |
| VCP/S — Semantics | [CSM-1 Grammar](./docs/content/CSM1_GRAMMAR_SPECIFICATION.md), [Composition](./docs/semantics/VCP_SEMANTICS_COMPOSITION.md) |
| VCP/A — Adaptation | [Adaptation](./docs/adaptation/VCP_ADAPTATION.md), [Context](./docs/context/VCP_CONTEXT_SPECIFICATION.md) |

### Core Security
[Encryption, Injection Scanning, Context Opacity, Revocation](./specs/core/security.md) | [Audit Chain](./specs/core/audit.md)

### Version History
See [CHANGELOG](./specs/CHANGELOG.md).

---

## Schemas

| Schema | Validates | Version |
|:---|:---|:---|
| [vcp-manifest-v1](./schemas/vcp-manifest-v1.schema.json) | Bundle manifests | v1.0 |
| [vcp-identity-token](./schemas/vcp-identity-token.schema.json) | Identity tokens | v1.0 |
| [vcp-semantics-csm1](./schemas/vcp-semantics-csm1.schema.json) | CSM-1 tokens | v1.0 |
| [vcp-adaptation-context](./schemas/vcp-adaptation-context.schema.json) | Adaptation context | v1.0 |
| [vcp-capability-handshake](./schemas/vcp-capability-handshake.schema.json) | Capability negotiation | **v3.1** |

Extension schemas are co-located: `specs/extensions/VCP-X-*/schema.json`.

---

## Governance

VCP is governed by a Technical Steering Committee (TSC) under a foundation-compatible model:

- **Decision process**: Lazy consensus, supermajority for spec changes
- **Contribution**: DCO (Developer Certificate of Origin) sign-off
- **Extension proposals**: Via the [VEP process](./GOVERNANCE.md)
- **IP license**: MIT License with Agentic AI Foundation transfer clause

See [GOVERNANCE.md](./GOVERNANCE.md) for the full charter and [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines.

### Filed VEPs

| VEP | Title | Status |
|-----|-------|--------|
| [VEP-0001](./veps/VEP-0001-extension-model.md) | Extension Model Architecture | Accepted |
| [VEP-0002](./veps/VEP-0002-capability-negotiation.md) | Capability Negotiation Protocol | Accepted |
| [VEP-0003](./veps/VEP-0003-mcp-bridge.md) | VCP-over-MCP Bridge | Accepted |

---

## SDKs

Reference implementations live in the [VCP-SDK repository](https://github.com/Creed-Space/vcp-sdk):

| Language | Version | Status |
|:---|:---|:---|
| **Python** | 3.1.0 | Reference implementation |
| **Rust** | 3.1.0 | High-performance / WASM |
| **TypeScript** | 3.1.0 | Browser-side |

---

## Roadmap

- **VCP Inspector**: Interactive web tool for decoding/encoding VCP tokens ([planned](https://github.com/Creed-Space/VCP-Inspector))
- **VCP Examples**: 10 runnable examples covering all extensions ([planned](https://github.com/Creed-Space/VCP-Examples))
- **Anti-drift CI**: Automated spec-implementation version sync checks
- **Agentic AI Foundation**: Transfer of VCP governance to neutral foundation

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

- **Typo / Clarification**: Open a PR directly
- **Spec Change**: Follow the [VEP process](./GOVERNANCE.md)
- **Extension Proposal**: Use the [VEP template](./CONTRIBUTING.md#3-extension-proposal-template)

Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) before participating.

---

## License

This project is licensed under the [MIT License](./LICENSE).

---

## Authors

Nell Watson, Elena Ajayi, Filip Alimpić, Awwab Mahdi, Blake Wells, Claude (Anthropic)

A **[Creed Space](https://creedspace.com)** project, developed for contribution to the **[Agentic AI Foundation](https://agenticaifoundation.org)**.

---

<div align="center">

*Context that travels with you.*

[Website](https://www.valuecontextprotocol.org) | [SDK](https://github.com/Creed-Space/vcp-sdk) | [Spec](./specs/VCP_SPECIFICATION_v3.1.md)

</div>
